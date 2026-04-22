from flask_wtf import FlaskForm
from wtforms import HiddenField, TextAreaField, SubmitField
from wtforms.validators import Length, Optional


class ClockInForm(FlaskForm):
    latitude = HiddenField("Latitude")
    longitude = HiddenField("Longitude")
    submit = SubmitField("Clock In")


class ClockOutForm(FlaskForm):
    latitude = HiddenField("Latitude")
    longitude = HiddenField("Longitude")
    early_departure_reason = TextAreaField("Early Departure Reason", validators=[Optional(), Length(max=400)])
    submit = SubmitField("Clock Out")
