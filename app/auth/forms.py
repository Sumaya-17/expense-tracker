from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Regexp


class RegistrationForm(FlaskForm):
    name = StringField("Full name", validators=[DataRequired(), Length(max=100)])
    username = StringField("Username", validators=[DataRequired(), Length(min=3, max=30), Regexp(r"^[A-Za-z0-9_]+$")])
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=8, max=128)])
    confirm_password = PasswordField("Confirm password", validators=[DataRequired(), EqualTo("password")])
    submit = SubmitField("Create account")


class LoginForm(FlaskForm):
    username = StringField("Username or email", validators=[DataRequired(), Length(max=120)])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Sign in")


class ForgotPasswordForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=120)])
    submit = SubmitField("Request reset link")
