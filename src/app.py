import os
from flask import Flask, flash, render_template, redirect, request, url_for, send_from_directory
from flask_login import LoginManager, login_required, current_user
from login_manager_setup import setup_login_manager
from werkzeug.utils import secure_filename
from PIL import Image
import time

from dao import palchi_dao, spettacoli_dao, biglietti_dao

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
STATIC_DIR = os.path.join(BASE_DIR, "static")
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")

# initialize the application
app = Flask(__name__, template_folder=TEMPLATES_DIR, static_folder=STATIC_DIR)
setup_login_manager(app)
app.config["SECRET_KEY"] = "g3t_YoUr_s0uNd"
app.config["UPLOAD_FOLDER"] = UPLOAD_DIR

# route for homepage
@app.route("/")
def home():
    shows_one = spettacoli_dao.get_shows_filtered(1, "all", "all", published=1)
    shows_two = spettacoli_dao.get_shows_filtered(2, "all", "all", published=1)
    shows_three = spettacoli_dao.get_shows_filtered(3, "all", "all", published=1)
    return render_template("home.html", p_shows_one = shows_one, p_shows_two = shows_two, p_shows_three = shows_three)

# route for full program list (base, senza filtri)
@app.route("/program")
def program():
    page = request.args.get("page", default=1, type=int)
    day = request.args.get("day", default=0, type=int)
    stage = request.args.get("stage", default=-1, type=int)
    genre = request.args.get("genre", default="all", type=str)
    shows = spettacoli_dao.get_shows_filtered(day, stage, genre, published=1)

    per_page = 10
    start = (page - 1) * per_page
    end = start + per_page
    paginated_shows = shows[start:end]
    total_pages = (len(shows) + per_page - 1) // per_page

    return render_template("program.html", p_shows=paginated_shows, current_page=page, total_pages=total_pages)


# route to show all details about a single show
@app.route("/program/<artist_name>")
def artist(artist_name):
    artist_name = artist_name.replace("%20", " ")
    artist = spettacoli_dao.get_artist_by_name(artist_name)
    return render_template("artist.html", p_artist=artist)

# route for profile
@app.route("/profile")
@login_required
def profile():
    if current_user.tipo == "Basic":
        ticket = biglietti_dao.get_ticket_by_user_id(current_user.id)
        return render_template("profile_basic.html", p_ticket = ticket)
    else:
        published = spettacoli_dao.get_published()
        drafts = spettacoli_dao.get_drafts(current_user.id)
        return render_template("profile_staff.html", p_published = published, p_drafts = drafts)

# route to show all types of ticket
@app.route("/ticket-form")
@login_required
def ticket_page():
    # users can buy only one ticket, if they already got it, the form disappears and their ticket will be shown 
    ticket = biglietti_dao.get_ticket_by_user_id(current_user.id)
    if ticket:
        return render_template("ticket.html", p_ticket = ticket)
    return render_template("ticket.html", p_ticket_types = ("one_day", "two_days", "three_days"), p_n_days = "")

# route to buy a ticket
@app.route("/buy_ticket", methods=["POST"])
@login_required
def buy_ticket():
    ticket_type = request.form.get('ticket_type')
    
    if ticket_type == "three_days":
        start_day = "friday 20th"
    else:
        start_day = request.form.get('start_day')

    if not ticket_type or not start_day:
        flash("MISSING_REQUIRED_PARAMETERS")
        return redirect(url_for('ticket_page'))

    success, error = biglietti_dao.buy_ticket_for_user(current_user.id, ticket_type, start_day)
    
    if not success:
        flash(error)
        return redirect(url_for('ticket_page'))
    else:
        return redirect(url_for("profile"))

# route with form to create an event
@app.route("/event")
@login_required
def event_page():
    # check for logs by console
    if current_user.tipo == "Basic":
        return redirect(url_for("home"))

    drafts = spettacoli_dao.get_drafts(current_user.id)
    stages = palchi_dao.get_stages()

    # Converti i risultati in liste di dizionari (se non sono errori)
    if isinstance(drafts, list):
        drafts = [dict(row) for row in drafts]
    if isinstance(stages, list):
        stages = [dict(row) for row in stages]

    return render_template("create_event.html", p_drafts=drafts, p_stages=stages)


# route for creating an event
@app.route("/create_event", methods = ['POST'])
@login_required
def create_event():
    #TODO: quando parto da una bozza e pubblico l'evento devo modificare la bozza e settarla come pubblicata + salvare la foto in bozza
    #controllo della non sovrapposizione con altri eventi (SOLO TRA QUELLI GIA' PUBBLICATI) solo al momento della pubblicazione dell'evento
    # sarà valutato all'esame con due tab aperte, si inizia una transazione che si lascia a metà, si prenota uno slot concerto in quell'orario e si verifica che la prima non sia più possibile
    draft_id = request.form.get('draft_id')
    day = request.form.get('day')
    start_hour = request.form.get('start_hour')
    duration = request.form.get('duration')
    artist = request.form.get('artist')
    description = request.form.get('description') or None
    genre = request.form.get('genre') or None
    stage_name = request.form.get('stage')
    img = request.files.get('image')
    action = request.form.get('action')  # draft o publish
    published = 1 if action == 'publish' else 0

    required_fields = {
        "day": day,
        "start_hour": start_hour,
        "duration": duration,
        "artist": artist,
        "stage_name": stage_name,
    }

    if published:
        required_fields["description"] = description
        required_fields["genre"] = genre
        required_fields["img"] = img

    missing_fields = [name for name, value in required_fields.items() if not value]
    if missing_fields:
        flash(f"Missing required fields: {', '.join(missing_fields)}")
        return redirect(url_for('event_page'))

    db_img_path = None
    if img:
        PROFILE_IMG_HEIGHT = 423
        POST_IMG_WIDTH = 636
        ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf'}

        is_allowed_file = '.' in img.filename and img.filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
        if not is_allowed_file:
            flash(f"FILE_TYPE_NOT_ALLOWED_ERROR - Allowed extensions: {', '.join(ALLOWED_EXTENSIONS)}")
            return redirect(url_for('event_page'))
    
        original_filename = secure_filename(img.filename)
        new_filename = f"{int(time.time())}_{original_filename}"
        upload_path = os.path.join(app.config["UPLOAD_FOLDER"], new_filename)

        image = Image.open(img.stream)
        aspect_ratio = image.height / image.width
        new_height = int(POST_IMG_WIDTH * aspect_ratio)

        resized_image = image.resize((POST_IMG_WIDTH, new_height), Image.LANCZOS)
        resized_image.save(upload_path)

        img.save(upload_path)
        db_img_path = f"uploads/{new_filename}"

    if draft_id:
        success, error = spettacoli_dao.update_draft(
            draft_id, day, start_hour, duration, artist, description, db_img_path,
            genre, published, current_user.id, stage_name
        )
    else:
        success, error = spettacoli_dao.create_event(
            day, start_hour, duration, artist, description, db_img_path,
            genre, published, current_user.id, stage_name
        )
    if not success:
        flash(error)
        return redirect(url_for('event_page'))
    flash("EVENT_CREATED_WITH_SUCCESS")
    return redirect(url_for("home"))

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

# route for handling settings operations, such as setting up a new staff password, or sell out all remaining tickets
@app.route("/settings")
@login_required
def settings():
    return render_template("settings.html")

import auth

# handles every route in auth_bp
app.register_blueprint(auth.auth_bp)

if __name__ == "__main__":
    app.run(debug=True)
