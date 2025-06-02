# import module
from flask import Flask, flash, render_template, redirect, request, url_for

from flask_login import LoginManager, login_required, current_user

import spettacoli_dao, biglietti_dao, settings_dao

# Image module to preprocess the images uploaded by the users
from PIL import Image
PROFILE_IMG_HEIGHT = 130
POST_IMG_WIDTH = 300

# initialize the application
app = Flask(__name__)
app.config["SECRET_KEY"] = "g3t_YoUr_s0uNd"
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login" #redirect user to login() function when trying to acces a login_required page (so we won't have the 401 Unauthorized page)

# route for homepage
@app.route("/")
def home():
    #TODO: maybe set only (5) artist per day to be shown in home
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
    ticket_type = request.form.get('type')
    start_day = request.form.get('start_day')

    if not ticket_type or not start_day:
        flash("MISSING_REQUIRED_PARAMETERS")
        return redirect(url_for('ticket_page'))

    conn = settings_dao.get_connection()
    try:
        with conn:
            success, error = biglietti_dao.buy_ticket_for_user(current_user.id, ticket_type, start_day, conn)
            if not success:
                flash(error)
                return redirect(url_for('ticket_page'))
    except Exception as e:
        conn.rollback()
        flash('DATABASE_ERROR')
        return redirect(url_for('ticket_page'))
    finally:
        conn.close()
    flash("Biglietto acquistato con successo!")
    return redirect(url_for("profile"))

# route with form to create an event
@app.route("/event")
@login_required
def event_page():
    return render_template("create_event.html")

# route for creating an event
@app.route("/create-event", methods = ['POST'])
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
    stage_name = request.form.get('stage_name')
    creator_id = current_user.id
    
    #TODO: decide how many photos the website needs for each event (probabilmente ne basta una)
    #foto(s) = request.form.get('photo')    gestisci i(l) file, con il nome da formattare tramite timestamp e ripulito da caratteri dannosi

    required_fields = [day, start_hour, duration, artist, description, genre, published, stage_name]
    if not all(required_fields):
        flash("MISSING_REQUIRED_PARAMETERS")
        return redirect(url_for('event_page'))

    conn = settings_dao.get_connection()
    try:
        with conn:
            success, error = spettacoli_dao.create_event(conn, day, start_hour, duration, artist, description, genre, published, stage_name)
            if not success:
                flash(error)
                return redirect(url_for('event_page'))
    except Exception as e:
        conn.rollback()
        flash('DATABASE_ERROR')
        return redirect(url_for('event_page'))
    finally:
        conn.close()
    flash("EVENT_CREATED_WITH_SUCCESS")
    return redirect(url_for("profile"))

# route for handling settings operations, such as setting up a new staff password, or sell out all remaining tickets
@app.route("/settings")
@login_required
def settings():
    return render_template("settings.html")

if __name__ == "__main__":
    app.run(debug=True)