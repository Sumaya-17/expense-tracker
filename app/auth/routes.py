from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import current_user, login_user, logout_user
from sqlalchemy import or_
from .forms import ForgotPasswordForm, LoginForm, RegistrationForm
from ..extensions import db
from ..models import User

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))
    form = RegistrationForm()
    if form.validate_on_submit():
        username = form.username.data.strip().lower()
        email = form.email.data.strip().lower()
        if User.query.filter(or_(User.username == username, User.email == email)).first():
            flash("That username or email is already in use.", "danger")
        else:
            user = User(name=form.name.data.strip(), username=username, email=email)
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            login_user(user)
            flash("Your account is ready. Welcome to Ledgerly!", "success")
            return redirect(url_for("main.dashboard"))
    return render_template("auth/register.html", form=form)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))
    form = LoginForm()
    if form.validate_on_submit():
        identifier = form.username.data.strip().lower()
        user = User.query.filter(or_(User.username == identifier, User.email == identifier)).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash("Welcome back, {}.".format(user.name.split()[0]), "success")
            return redirect(url_for("main.dashboard"))
        flash("Invalid username/email or password.", "danger")
    return render_template("auth/login.html", form=form)


@auth_bp.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    """Safe placeholder until an email provider is configured."""
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        flash("If an account matches that email, a reset link will be sent when email delivery is configured.", "info")
        return redirect(url_for("auth.login"))
    return render_template("auth/forgot_password.html", form=form)


@auth_bp.post("/logout")
def logout():
    logout_user()
    flash("You have been signed out.", "info")
    return redirect(url_for("main.index"))
