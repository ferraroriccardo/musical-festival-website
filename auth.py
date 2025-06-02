from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from urllib.parse import urlparse, urljoin

import utenti_dao, settings_dao
from models import User

auth_bp = Blueprint("auth", __name__)  # handles separation of this module from app.py

# user loader
from app import login_manager

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

# security function to avoid open redirects
def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ("http", "https") and ref_url.netloc == test_url.netloc

# route for login page
@auth_bp.route("/login-form", methods=['GET'])
def login_page():
    return render_template("login.html")

# route to handle login data
@auth_bp.route("/login", methods=['POST'])
def login():
    email = request.form.get('email')
    password = request.form.get('password')
    
    # Validation
    if not email or not password:
        flash("MISSING_EMAIL_OR_PASSWORD_ERROR")
        return redirect(url_for("login_page"))
    elif "@" not in email:
        flash("INVALID_EMAIL_ERROR")
        return redirect(url_for("login_page"))

    user_data = utenti_dao.get_user_by_email(email)

    if not user_data:
        flash("EMAIL_NOT_FOUND_ERROR")
        return redirect(url_for("login_page"))
    elif not check_password_hash(user_data["password"], password):
        flash("WRONG_PASSWORD_ERROR")
        return redirect(url_for("login_page"))

    user = User(
        id=user_data["id"],
        email=user_data["email"],
        password=user_data["password"],
        tipo=user_data["tipo"],
        id_biglietto=user_data["id_biglietto"]
    )
    login_user(user)
    next_page = request.args.get("next")

    if next_page and is_safe_url(next_page):
        return redirect(next_page)
    else:
        return redirect(url_for("home"))

# route for logout
@auth_bp.route("/logout")
@login_required
def logout():
	logout_user()
	return redirect(url_for('home'))

# route for sign up
@auth_bp.route("/sign-up-form", methods=['GET'])
def signup_page():
    next_page = request.args.get("next") # gets the next page to render after the login. Can be None if we click directly to sign up
    return render_template("signup.html", p_type=("staff", "basic"), next=next_page)

# route to handle sign up data
@auth_bp.route("/signup", methods=['POST'])
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
    
    next_page = request.form.get("next")
    if next_page and is_safe_url(next_page):
        return redirect(next_page)
    else:
        return redirect(url_for("home"))
