# import module
from flask import Flask, flash, render_template, redirect, request, url_for

from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from models import User

from werkzeug.security import generate_password_hash, check_password_hash

import utenti_dao, spettacoli_dao, biglietti_dao

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
	user = User(id=db_user["id"],
		email=db_user["email"],
		password=db_user["password"],
		tipo=db_user["tipo"],
		id_biglietto=db_user["id_biglietto"],)
	return user

# route for homepage
@app.route("/")
def home():
    flash("prova")
    return render_template("home.html")

# route for login
@app.route("/login", methods=['POST'])
def login():
    email = request.form.get('email')
    password = request.form.get('password')
    type = request.form.get('type')

    hashed_password = generate_password_hash(password, method='sha256')
    #if (utenti_dao.get_user_by_email(email) != None)
    #    redirect(url_for("login.html"), error=USER_ALREADY_EXISTS_ERROR)
    
    # Validation
    if not email or not password:
        app.logger.warning("Form submitted with missing fields.")
    elif "@" not in email:
        app.logger.warning("Form submitted with invalid email: %s", email)
    else:
        app.logger.info("User subscribed successfully: %s", email)

    return redirect(url_for("home"))

# route for logout
@app.route("/logout")
@login_required
def logout():
	logout_user()
	return redirect(url_for('home'))

# route for sign up
@app.route("/signup", methods=['POST'])
def signup():
    #per registrarsi come organizzatore serve una password tipo FESTIVAL, da mettere nel README
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

@app.route("/buy_ticket", methods=["POST"])
@login_required
def buy_ticket():
    ticket_type = request.form.get('type')
    success, error = biglietti_dao.buy_ticket_for_user(current_user.id, ticket_type)
    if not success:
        flash(error)
        return redirect(url_for('ticket_page'))
    flash("Biglietto acquistato con successo!")
    return redirect(url_for("profile"))

if __name__ == "__main__":
    app.run(debug=True)