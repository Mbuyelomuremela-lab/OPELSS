from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, HiddenField
from wtforms.validators import DataRequired, Email, Length


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6, max=128)])
    latitude = HiddenField("Latitude")
    longitude = HiddenField("Longitude")
    submit = SubmitField("Sign In")


class PasswordResetForm(FlaskForm):
    current_password = PasswordField("Current Password", validators=[DataRequired(), Length(min=6, max=128)])
    new_password = PasswordField("New Password", validators=[DataRequired(), Length(min=6, max=128)])
    submit = SubmitField("Reset Password")
