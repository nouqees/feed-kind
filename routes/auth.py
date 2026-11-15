from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash

from extensions import db
from models.user import User
from utils.validators import is_valid_email

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

ROLE_DASHBOARD = {
    User.ROLE_ADMIN: "admin.dashboard",
    User.ROLE_DONOR: "donor.dashboard",
    User.ROLE_NGO: "ngo.dashboard",
}


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")
        phone = request.form.get("phone", "").strip()
        address = request.form.get("address", "").strip()
        role = request.form.get("role", "")

        errors = []
        if not name:
            errors.append("Name is required.")
        if not is_valid_email(email):
            errors.append("Enter a valid email address.")
        if len(password) < 6:
            errors.append("Password must be at least 6 characters.")
        if password != confirm_password:
            errors.append("Passwords do not match.")
        if role not in (User.ROLE_DONOR, User.ROLE_NGO):
            errors.append("Select whether you are registering as a Food Donor or an NGO.")
        if email and User.query.filter_by(email=email).first():
            errors.append("An account with this email already exists.")

        if errors:
            for error in errors:
                flash(error, "error")
            return render_template("auth/register.html", form=request.form)

        user = User(
            name=name,
            email=email,
            password_hash=generate_password_hash(password, method="pbkdf2:sha256"),
            phone=phone,
            address=address,
            role=role,
        )
        db.session.add(user)
        db.session.commit()

        flash("Registration successful. Please log in.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/register.html", form={})


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        user = User.query.filter_by(email=email).first()

        if not user or not check_password_hash(user.password_hash, password):
            flash("Invalid email or password.", "error")
            return render_template("auth/login.html", email=email)

        if not user.is_active:
            flash("Your account has been deactivated. Contact the admin.", "error")
            return render_template("auth/login.html", email=email)

        session["user_id"] = user.id
        session["user_name"] = user.name
        session["user_role"] = user.role

        flash(f"Welcome back, {user.name}!", "success")
        return redirect(url_for(ROLE_DASHBOARD[user.role]))

    return render_template("auth/login.html", email="")


@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("main.home"))
