# import module
from flask import Flask, flash, render_template, redirect, request, url_for

from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from models import User

from werkzeug.security import generate_password_hash, check_password_hash

import utenti_dao, spettacoli_dao, biglietti_dao, static_dao

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
    static_dao.set_staff_passw("FESTIVAL")
    print("set password")
    return render_template("home.html")

# route to handle login data
@app.route("/login", methods=['POST'])
def login():
    email = request.form.get('email')
    password = request.form.get('password')

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

# route for login page
@app.route("/login-form", methods=['GET'])
def login_page():
    return render_template("login.html")

# route for logout
@app.route("/logout")
@login_required
def logout():
	logout_user()
	return redirect(url_for('home'))

# route to handle sign up data
@app.route("/signup", methods=['POST'])
def signup():
    #per registrarsi come organizzatore serve una password tipo FESTIVAL, da mettere nel README
    email = request.form.get('email')
    password1 = request.form.get('password1')
    password2 = request.form.get('password2')
    type = request.form.get('type')
    staff_password = request.form.get('staff_password')

    if not email or not password or staff_password:
        flash("MISSING_EMAIL_OR_PASSWORD_ERROR")
        return redirect(url_for("login"))
    elif "@" not in email:
        flash("INVALID_EMAIL_ERROR")
        return redirect(url_for("login"))

    user_data = utenti_dao.get_user_by_email(email)

    if not user_data:
        flash("EMAIL_NOT_FOUND_ERROR")
        return redirect(url_for("login"))
    elif not check_password_hash(user_data["password"], password1):
        flash("WRONG_PASSWORD_ERROR")
    if type == "staff" and not check_password_hash(static_dao.get_staff_password(), staff_password):
        flash("STAFF_PASSWORD_ERROR")
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

# route for sign up
@app.route("/sign-up-form", methods=['GET'])
def signup_page():
    return render_template("signup.html")

# route for profile
@login_required
@app.route("/profile")
def profile():
    return render_template("profile.html")

# route for buying ticket
@login_required
@app.route("/ticket")
def ticket():
    #limite di 200 persone, non salvarlo nel database, ma fai un COUNT(event_id)
    return render_template("ticket.html")

# route for event
@app.route("/event")
def event():
    return render_template("event.html")

# route for creating an event
@login_required
@app.route("/create-event")
def create_event():
    #controllo della non sovrapposizione con altri eventi (SOLO TRA QUELLI GIA' PUBBLICATI) solo al momento della pubblicazione dell'evento
    # sarà valutato all'esame con due tab aperte, si inizia una transazione che si lascia a metà, si prenota uno slot concerto in quell'orario e si verifica che la prima non sia più possibile
    return render_template("create_event.html")

if __name__ == "__main__":
    app.run(debug=True)