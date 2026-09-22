from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import current_user, login_required
from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, SubmitField
from wtforms.validators import DataRequired, Email, Length
from ..extensions import db
from ..models import User

profile_bp = Blueprint("profile", __name__)


class ProfileForm(FlaskForm):
    name = StringField("Full name", validators=[DataRequired(), Length(max=100)])
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=120)])
    currency_code = SelectField("Currency", choices=[("INR", "Indian Rupee (₹)")])
    submit = SubmitField("Save changes")


@profile_bp.route("/", methods=["GET", "POST"])
@login_required
def index():
    form = ProfileForm(obj=current_user)
    if form.validate_on_submit():
        email = form.email.data.strip().lower()
        exists = User.query.filter(User.email == email, User.id != current_user.id).first()
        if exists: flash("That email is already in use.", "danger")
        else:
            current_user.name, current_user.email, current_user.currency_code = form.name.data.strip(), email, form.currency_code.data
            db.session.commit(); flash("Profile updated.", "success")
            return redirect(url_for("profile.index"))
    return render_template("profile/index.html", form=form)
