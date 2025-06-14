import os
from flask import Flask, flash, render_template, redirect, request, url_for, send_from_directory
from flask_login import login_required, current_user
from login_manager_setup import setup_login_manager
from werkzeug.utils import secure_filename
from urllib.parse import unquote
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

def normalize_error(message):
    return message.lower().replace('_', ' ')

app.jinja_env.filters['normalize_error'] = normalize_error

# route for homepage
@app.route("/")
def home():
    shows_one = spettacoli_dao.get_shows_filtered(1, "all", "all", published=1)
    shows_two = spettacoli_dao.get_shows_filtered(2, "all", "all", published=1)
    shows_three = spettacoli_dao.get_shows_filtered(3, "all", "all", published=1)
    return render_template("home.html", p_shows_one = shows_one, p_shows_two = shows_two, p_shows_three = shows_three)

# route for full program list
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

    stages = palchi_dao.get_stages()
    genres = spettacoli_dao.get_genres()

    selected = {"day": day, "stage": stage, "genre":genre}

    return render_template("program.html", p_shows=paginated_shows, current_page=page, total_pages=total_pages, p_stages=stages, p_genres=genres, p_selected=selected)


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
    page = request.args.get("page", default=1, type=int)
    per_page = 10
    if current_user.tipo == "Basic":
        ticket = biglietti_dao.get_ticket_by_user_id(current_user.id)
        return render_template("profile_basic.html", p_ticket = ticket)
    else:
        published = spettacoli_dao.get_published(current_user.id)
        drafts = spettacoli_dao.get_drafts(current_user.id)

        start = (page - 1) * per_page
        end = start + per_page
        paginated_published = published[start:end]
        paginated_drafts = drafts[start:end]
        total_published_pages = (len(published) + per_page - 1) // per_page
        total_drafts_pages = (len(drafts) + per_page - 1) // per_page
        return render_template(
            "profile_staff.html",
            p_published = paginated_published,
            p_drafts = paginated_drafts,
            current_page = page,
            total_published_pages = total_published_pages,
            total_drafts_pages = total_drafts_pages
        )

# route to show all types of ticket
@app.route("/ticket-form")
@login_required
def ticket_page():
    ticket = biglietti_dao.get_ticket_by_user_id(current_user.id)
    sells = biglietti_dao.get_sells()
    if ticket:
        return render_template("ticket.html", p_ticket = ticket, p_sells=sells)
    return render_template("ticket.html", p_ticket_types = ("one_day", "two_days", "three_days"), p_sells = sells)

# route to buy a ticket
@app.route("/buy_ticket", methods=["POST"])
@login_required
def buy_ticket():
    ticket_type = request.form.get('ticket_type')
    if ticket_type == "three_days":
        start_day = "friday 20th"
    else:
        start_day = request.form.get('start_day')
    errors = []
    if not ticket_type or not start_day:
        errors.append("MISSING_REQUIRED_PARAMETERS")
    success, error = (False, None)
    if not errors:
        success, error = biglietti_dao.buy_ticket_for_user(current_user.id, ticket_type, start_day)
        if not success:
            errors.append(error)
    if errors:
        ticket = biglietti_dao.get_ticket_by_user_id(current_user.id)
        sells = biglietti_dao.get_sells()
        return render_template("ticket.html", p_ticket=ticket, p_ticket_types=("one_day", "two_days", "three_days"), p_sells=sells, p_errors=errors)
    else:
        return redirect(url_for("profile"))

# route with form to create an event
@app.route("/event")
@login_required
def event_page():
    page = request.args.get("page", default=1, type=int)
    per_page = 10
    if current_user.tipo == "Basic":
        return redirect(url_for("home"))

    drafts = spettacoli_dao.get_drafts(current_user.id)
    stages = palchi_dao.get_stages()

    if isinstance(drafts, list):
        drafts = [dict(row) for row in drafts]
    if isinstance(stages, list):
        stages = [dict(row) for row in stages]

    start = (page - 1) * per_page
    end = start + per_page
    paginated_drafts = drafts[start:end]
    total_drafts_pages = (len(drafts) + per_page - 1) // per_page

    p_day = request.args.get('day')
    p_start_hour = request.args.get('start_hour')
    p_duration = request.args.get('duration')
    p_artist = request.args.get('artist_name')
    p_description = request.args.get('description')
    p_playlist_link = request.args.get('playlist_link')
    p_genre = request.args.get('genre')
    stage_id = request.args.get('stage_id')
    p_stage = None
    p_draft_id = request.args.get('draft_id')

    if stage_id:
        palco = next((s for s in stages if str(s['id']) == str(stage_id)), None)
        p_stage = palco['nome'] if palco else None

    return render_template(
        "create_event.html",
        p_drafts=paginated_drafts,
        p_stages=stages,
        p_day=p_day or None,
        p_start_hour=p_start_hour or None,
        p_duration=p_duration or None,
        p_artist=p_artist or None,
        p_description=p_description or None,
        p_playlist_link=p_playlist_link or None,
        p_genre=p_genre or None,
        p_stage=p_stage or None,
        p_draft_id=p_draft_id or '',
        current_page=page,
        total_drafts_pages=total_drafts_pages
    )


# route for creating an event
@app.route("/create_event", methods = ['POST', 'GET'])
@login_required
def create_event():
    draft_id = request.form.get('draft_id')
    day = request.form.get('day')
    start_hour = request.form.get('start_hour')
    duration = request.form.get('duration')
    artist = unquote(request.form.get('artist'))
    description = request.form.get('description') or None
    playlist_link = request.form.get('playlist_link') or None
    genre = request.form.get('genre') or None
    stage_name = request.form.get('stage')
    img = request.files.get('image')
    action = request.form.get('action')  # draft or publish
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
    errors = []
    if missing_fields:
        errors.append(f"MISSING_FIELDS_ERROR: {', '.join(missing_fields)}")
        new_drafts = spettacoli_dao.get_drafts(current_user.id)
        new_stages = palchi_dao.get_stages()
        if isinstance(new_drafts, list):
            new_drafts = [dict(row) for row in new_drafts]
        if isinstance(new_stages, list):
            new_stages = [dict(row) for row in new_stages]
        return render_template(
            "create_event.html",
            p_drafts=new_drafts,
            p_stages=new_stages,
            p_day=day,
            p_start_hour=start_hour,
            p_duration=duration,
            p_artist=artist,
            p_description=description,
            p_playlist_link=playlist_link or None,
            p_genre=genre,
            p_stage=stage_name,
            p_errors=errors
        )

    # Determine minimum max-dimension among all carousel images
    carousel_dir = app.config["UPLOAD_FOLDER"]
    min_max_dim = None
    for fname in os.listdir(carousel_dir):
        if fname.lower().endswith((".jpg", ".jpeg", ".png", ".gif")):
            try:
                img_path = os.path.join(carousel_dir, fname)
                with Image.open(img_path) as im:
                    w, h = im.size
                    max_dim = max(w, h)
                    if min_max_dim is None or max_dim < min_max_dim:
                        min_max_dim = max_dim
            except Exception:
                continue
    if min_max_dim is None:
        min_max_dim = 800
    db_img_path = None
    if img:
        ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf'}
        is_allowed_file = '.' in img.filename and img.filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
        if not is_allowed_file:
            errors.append(f"FILE_TYPE_NOT_ALLOWED_ERROR - Allowed extensions: {', '.join(ALLOWED_EXTENSIONS)}")
            return render_template(
                "create_event.html",
                p_drafts=spettacoli_dao.get_drafts(current_user.id),
                p_stages=palchi_dao.get_stages(),
                p_day=day,
                p_start_hour=start_hour,
                p_duration=duration,
                p_artist=artist,
                p_description=description,
                p_playlist_link=playlist_link or None,
                p_genre=genre,
                p_stage=stage_name,
                p_errors=errors
            )
        original_filename = secure_filename(img.filename)
        new_filename = f"{int(time.time())}_{original_filename}"
        upload_path = os.path.join(app.config["UPLOAD_FOLDER"], new_filename)
        img.save(upload_path)
        # Resize image to min_max_dim
        try:
            with Image.open(upload_path) as im:
                w, h = im.size
                scale = min(min_max_dim / w, min_max_dim / h)
                new_size = (int(w * scale), int(h * scale))
                im = im.resize(new_size, Image.LANCZOS)
                im.save(upload_path)
        except Exception:
            errors.append("IMAGE_RESIZE_ERROR")
        db_img_path = f"uploads/{new_filename}"

    # DRAFT LOGIC: check if draft_id is present and valid for this user
    draft_id_valid = False
    if draft_id:
        try:
            draft_id_int = int(draft_id)
            draft_id_valid = spettacoli_dao.draft_exists_for_user(draft_id_int, current_user.id)
        except Exception:
            draft_id_valid = False

    if not published:
        # Always check for overlap with published events
        stage_id = palchi_dao.get_palco_by_name(stage_name)
        if stage_id is None:
            errors.append("STAGE_NOT_FOUND")
        elif spettacoli_dao.exist_overlapping_published_shows(day, start_hour, duration, stage_id, None, exclude_id=draft_id if draft_id_valid else None):
            errors.append("SHOW_SLOT_ALREADY_OCCUPIED")
        if errors:
            new_drafts = spettacoli_dao.get_drafts(current_user.id)
            new_stages = palchi_dao.get_stages()
            if isinstance(new_drafts, list):
                new_drafts = [dict(row) for row in new_drafts]
            if isinstance(new_stages, list):
                new_stages = [dict(row) for row in new_stages]
            return render_template(
                "create_event.html",
                p_drafts=new_drafts,
                p_stages=new_stages,
                p_day=day,
                p_start_hour=start_hour,
                p_duration=duration,
                p_artist=artist,
                p_description=description,
                p_playlist_link=playlist_link or None,
                p_genre=genre,
                p_stage=stage_name,
                p_errors=errors
            )

    # Save or update draft/event
    if not published:
        if draft_id_valid:
            success, error = spettacoli_dao.update_draft(
                draft_id, day, start_hour, duration, artist, description, playlist_link, db_img_path,
                genre, published, current_user.id, stage_name
            )
        else:
            success, error = spettacoli_dao.create_event(
                day, start_hour, duration, artist, description, playlist_link, db_img_path,
                genre, published, current_user.id, stage_name
            )
    else:
        # Publishing: always create a new event (not a draft update)
        success, error = spettacoli_dao.create_event(
            day, start_hour, duration, artist, description, playlist_link, db_img_path,
            genre, published, current_user.id, stage_name
        )
    if not success:
        errors.append(error)
        new_drafts = spettacoli_dao.get_drafts(current_user.id)
        new_stages = palchi_dao.get_stages()
        if isinstance(new_drafts, list):
            new_drafts = [dict(row) for row in new_drafts]
        if isinstance(new_stages, list):
            new_stages = [dict(row) for row in new_stages]
        return render_template(
            "create_event.html",
            p_drafts=new_drafts,
            p_stages=new_stages,
            p_day=day,
            p_start_hour=start_hour,
            p_duration=duration,
            p_artist=artist,
            p_description=description,
            p_playlist_link=playlist_link,
            p_genre=genre,
            p_stage=stage_name,
            p_errors=errors
        )
    return redirect(url_for("home"))

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

import auth

# handles every route in auth_bp
app.register_blueprint(auth.auth_bp)

if __name__ == "__main__":
    app.run(debug=True)
