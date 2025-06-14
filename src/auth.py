from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from urllib.parse import urlparse, urljoin

import dao.utenti_dao as utenti_dao
import dao.settings_dao as settings_dao
from models import User

auth_bp = Blueprint("auth", __name__)  # handles separation of this module from app.py

# security function to avoid open redirects
def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ("http", "https") and ref_url.netloc == test_url.netloc

# route for login page
@auth_bp.route("/login-form", methods=['GET'])
def login_page():
    return render_template("login.html", current_file="login.html")

# route to handle login data
@auth_bp.route("/login", methods=['POST'])
def login():
    email = request.form.get('email')
    password = request.form.get('password')
    next_page = request.form.get('next') or request.args.get('next')
    errors = []
    # Validation
    if not email or not password:
        errors.append("MISSING_EMAIL_OR_PASSWORD_ERROR")
    elif "@" not in email:
        errors.append("INVALID_EMAIL_ERROR")

    user_data = utenti_dao.get_user_by_email(email) if not errors else None

    if not errors and not user_data:
        errors.append("EMAIL_NOT_FOUND_ERROR")
    elif not errors and not check_password_hash(user_data["password"], password):
        errors.append("WRONG_PASSWORD_ERROR")

    if errors:
        return render_template("login.html", p_errors=errors, current_file="login.html", request=request)

    user = User(
        id=user_data["id"],
        nome=user_data["nome"],
        email=user_data["email"],
        password=user_data["password"],
        tipo=user_data["tipo"],
        id_biglietto=user_data["id_biglietto"]
    )
    login_user(user)

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
    next_page = request.args.get("next") or request.args.get("next_page")
    return render_template("signup.html", p_type=("Basic", "Staff"), next=next_page, current_file="login.html")

# route to handle sign up data
@auth_bp.route("/signup", methods=['POST'])
def signup():
    name = request.form.get('name')
    email = request.form.get('email')
    password1 = request.form.get('password1')
    password2 = request.form.get('password2')
    type = request.form.get('type')
    staff_password = request.form.get('staff_password')
    errors = []
    if not name:
        errors.append("MISSING_NAME_ERROR")
    if not email or not password1 or not password2:
        errors.append("MISSING_EMAIL_OR_PASSWORD_ERROR")
    if password1 != password2:
        errors.append("UNMATCHING_PASSWORDS_ERROR")
    elif "@" not in email:
        errors.append("INVALID_EMAIL_ERROR")

    user_data = utenti_dao.get_user_by_email(email) if not errors else None
    if not errors and user_data:
        errors.append("EMAIL_ALREADY_REGISTERED_ERROR")
    staff_hash = settings_dao.get_staff_passw() if not errors else None
    if not errors and type == "staff" and not check_password_hash(staff_hash, staff_password):
        errors.append("STAFF_PASSWORD_ERROR")

    if errors:
        return render_template("signup.html", p_type=("Basic", "Staff"), p_errors=errors, current_file="login.html", request=request)

    hashed_passw = generate_password_hash(password1, method='pbkdf2:sha256')
    utenti_dao.create_user(name, email, hashed_passw, type)
    user = utenti_dao.get_user_by_email(email)
    param_user = User(
        id=user["id"],
        nome=user["nome"],
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
