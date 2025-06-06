import os
from flask import Flask, flash, render_template, redirect, request, url_for
from flask_login import LoginManager, login_required, current_user
from login_manager_setup import setup_login_manager

from dao import palchi_dao, spettacoli_dao, biglietti_dao

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
STATIC_DIR = os.path.join(BASE_DIR, "static")

# Image module to preprocess the images uploaded by the users
from PIL import Image
PROFILE_IMG_HEIGHT = 130
POST_IMG_WIDTH = 300

# initialize the application
app = Flask(__name__, template_folder=TEMPLATES_DIR, static_folder=STATIC_DIR)
setup_login_manager(app)
app.config["SECRET_KEY"] = "g3t_YoUr_s0uNd"

# route for homepage
@app.route("/")
def home():
    shows = spettacoli_dao.get_shows()
    return render_template("home.html", p_shows = shows)

# route for full program list (base, senza filtri)
@app.route("/program")
def program():
    shows = spettacoli_dao.get_shows()
    return render_template("program.html", p_shows=shows)

# route per programma filtrato (con parametri GET)
@app.route("/program/filter")
def program_filtered():
    giorno = request.args.get('giorno')
    palco = request.args.get('palco')
    genere = request.args.get('genere')
    shows = spettacoli_dao.get_shows_filtered(giorno, palco, genere)
    return render_template("program.html", p_shows=shows)

# route for profile
@app.route("/profile")
@login_required
def profile():
    ticket = biglietti_dao.get_ticket_by_user_id(current_user.id)
    if ticket:
        return render_template("profile.html", p_ticket = ticket)
    return render_template("profile.html")

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
    #controllo della non sovrapposizione con altri eventi (SOLO TRA QUELLI GIA' PUBBLICATI) solo al momento della pubblicazione dell'evento
    # sarà valutato all'esame con due tab aperte, si inizia una transazione che si lascia a metà, si prenota uno slot concerto in quell'orario e si verifica che la prima non sia più possibile
    day = request.form.get('day')
    start_hour = request.form.get('start_hour')
    duration = request.form.get('duration')
    artist = request.form.get('artist')
    description = request.form.get('description')
    genre = request.form.get('genre')
    published = request.form.get('published')
    stage_name = request.form.get('stage')
    
    #TODO: decide how many photos the website needs for each event (probabilmente ne basta una)
    #foto(s) = request.form.get('photo')    gestisci i(l) file, con il nome da formattare tramite timestamp e ripulito da caratteri dannosi

    required_fields = {
        "day": day,
        "start_hour": start_hour,
        "duration": duration,
        "artist": artist,
        "description": description,
        "genre": genre,
        "published": published,
        "stage_name": stage_name
    }

    missing_fields = [name for name, value in required_fields.items() if not value]

    if missing_fields:
        flash(f"Missing required fields: {', '.join(missing_fields)}")
        return redirect(url_for('event_page'))

    success, error = spettacoli_dao.create_event(day, start_hour, duration, artist, description, genre, published, current_user.id, stage_name)
    if not success:
        flash(error)
        return redirect(url_for('event_page'))
    flash("EVENT_CREATED_WITH_SUCCESS")
    return redirect(url_for("home"))

# route for handling settings operations, such as setting up a new staff password, or sell out all remaining tickets
@app.route("/settings")
@login_required
def settings():
    return render_template("settings.html")

import auth

app.register_blueprint(auth.auth_bp)  # handles every route in auth_bp

if __name__ == "__main__":
    app.run(debug=True)