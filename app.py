# import module
from flask import Flask, flash, render_template, redirect, request, url_for

from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from models import User

from werkzeug.security import generate_password_hash, check_password_hash

import utenti_dao, spettacoli_dao, biglietti_dao, settings_dao

# Image module to preprocess the images uploaded by the users
from PIL import Image
PROFILE_IMG_HEIGHT = 130
POST_IMG_WIDTH = 300

# initialize the application
app = Flask(__name__)
app.config["SECRET_KEY"] = "g3t_YoUr_s0uNd"
login_manager = LoginManager()
login_manager.init_app(app)

# user object getter function
@login_manager.user_loader
def load_user(user_id):
    db_user = utenti_dao.get_user_by_id(user_id)

    if db_user is None:
        return None 
    user = User(
        id=db_user["id"],
        email=db_user["email"],
        password=db_user["password"],
        tipo=db_user["tipo"],
        id_biglietto=db_user["id_biglietto"]
    )
    return user

# route for homepage
@app.route("/")
def home():
    shows = spettacoli_dao.get_shows()
    return render_template("home.html", p_shows = shows)

# route for login page
@app.route("/login-form", methods=['GET'])
def login_page():
    return render_template("login.html")

# route to handle login data
@app.route("/login", methods=['POST'])
def login():
    email = request.form.get('email')
    password = request.form.get('password')
    
    # Validation
    if not email or not password:
        flash("MISSING_EMAIL_OR_PASSWORD_ERROR")
        return redirect(url_for("login"))
    elif "@" not in email:
        flash("INVALID_EMAIL_ERROR")
        return redirect(url_for("login"))

    user_data = utenti_dao.get_user_by_email(email)

    if not user_data:
        flash("EMAIL_NOT_FOUND_ERROR")
        return redirect(url_for("login"))
    elif not check_password_hash(user_data["password"], password):
        flash("WRONG_PASSWORD_ERROR")
        return redirect(url_for("login"))

    user = User(
        id=user_data["id"],
        email=user_data["email"],
        password=user_data["password"],
        tipo=user_data["tipo"],
        id_biglietto=user_data["id_biglietto"]
    )
    login_user(user)
    return redirect(url_for("home"))

# route for logout
@app.route("/logout")
@login_required
def logout():
	logout_user()
	return redirect(url_for('home'))

# route for sign up
@app.route("/sign-up-form", methods=['GET'])
def signup_page():
    return render_template("signup.html")

# route to handle sign up data
@app.route("/signup", methods=['POST'])
def signup():
    email = request.form.get('email')
    password1 = request.form.get('password1')
    password2 = request.form.get('password2')
    type = request.form.get('type')
    staff_password = request.form.get('staff_password')
    hashed_passw = generate_password_hash(password1)

    if not email or not password1 or not password2:
        flash("MISSING_EMAIL_OR_PASSWORD_ERROR")
        return redirect(url_for("signup_page"))
    if password1 != password2:
        flash("UNMATCHING_PASSWORDS_ERROR")
        return redirect(url_for("signup_page"))
    elif "@" not in email:
        flash("INVALID_EMAIL_ERROR")
        return redirect(url_for("signup_page"))

    user_data = utenti_dao.get_user_by_email(email)
    if user_data:
        flash("EMAIL_ALREADY_REGISTERED_ERROR")
        return redirect(url_for("signup_page"))
    
    staff_hash = settings_dao.get_staff_password()
    if type == "staff" and not check_password_hash(staff_hash[0], staff_password):
        flash("STAFF_PASSWORD_ERROR")
        return redirect(url_for("signup_page"))

    utenti_dao.create_user(email, hashed_passw, type)
    user = utenti_dao.get_user_by_email(email)
    param_user = User(
        id=user["id"],
        email=user["email"],
        password=user["password"],
        tipo=user["tipo"],
        id_biglietto=user["id_biglietto"]
    )

    login_user(param_user)
    return redirect(url_for("home"))

# route for profile
@login_required
@app.route("/profile")
def profile():
    ticket = biglietti_dao.get_ticket_by_email(current_user.email)
    if ticket:
        return render_template("profile.html", p_ticket = ticket)
    return render_template("profile.html")

# route to show all types of ticket
@login_required
@app.route("/ticket-form")
def ticket_page():
    return render_template("ticket.html")

# route to buy a ticket
@login_required
@app.route("/buy_ticket", methods=["POST"])
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
@login_required
@app.route("/event")
def event_page():
    return render_template("event.html")

# route for creating an event
@login_required
@app.route("/create-event")
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
    stage = request.form.get('stage')
    creator_id = current_user.id
    
    #TODO: decide how many photos the website needs for each event
    #foto(s) = request.form.get('photo')    gestisci i(l) file, con il nome da formattare tramite timestamp e ripulito da caratteri dannosi

    required_fields = [day, start_hour, duration, artist, description, genre, published, stage]
    if not all(required_fields):
        flash("MISSING_REQUIRED_PARAMETERS")
        return redirect(url_for('event_page'))

    conn = settings_dao.get_connection()
    try:
        with conn:
            success, error = spettacoli_dao.create_event(conn, day, start_hour, duration, artist, description, genre, published, stage)
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
@login_required
@app.route("/settings")
def settings():
    return render_template("settings.html")

if __name__ == "__main__":
    app.run(debug=True)