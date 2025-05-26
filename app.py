# import module
from flask import Flask, render_template, request, redirect, url_for

from flask_login import (
    LoginManager,
    login_user,
    login_required,
    logout_user,
    current_user,
)
from werkzeug.security import generate_password_hash, check_password_hash

import posts_dao, commenti_dao, utenti_dao

from models import User

# Image module to preprocess the images uploaded by the users
from PIL import Image
PROFILE_IMG_HEIGHT = 130
POST_IMG_WIDTH = 300

# initialize the application
app = Flask(__name__)

app.config["SECRET_KEY"] = "Secret key del social network"

login_manager = LoginManager()
login_manager.init_app(app)

# route for homepage
@app.route("/")
def home():
    render_template("home.html")

# route for login
@app.login("/login")
def login():
    render_template("login.html")

# route for sign up
@app.route("/signup")
def signup():
    render_template("signup.html")

# route for profile
@app.route("/profile")
def profile():
    render_template("profile.html")

# route for event
@app.route("/event")
def event():
    render_template("event.html")

# route for creating an event
@app.route("/create-event")
def create_event():
    render_template("create_event.html")