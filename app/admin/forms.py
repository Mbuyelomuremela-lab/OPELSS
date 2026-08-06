from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, BooleanField, SubmitField, FloatField
from wtforms.validators import DataRequired, Length, Email, Optional, Regexp
from app.permissions import ROLE_CHOICES


class ProvinceForm(FlaskForm):
    name = StringField("Province Name", validators=[DataRequired(), Length(max=120)])
    submit = SubmitField("Add Province")


class LabForm(FlaskForm):
    name = StringField("Lab Name", validators=[DataRequired(), Length(max=120)])
    province_id = SelectField("Province", coerce=int, validators=[DataRequired()])
    latitude = FloatField("Latitude", validators=[DataRequired()])
    longitude = FloatField("Longitude", validators=[DataRequired()])
    radius_meters = FloatField("Radius (meters)", validators=[DataRequired()])
    submit = SubmitField("Create Lab")


class UserForm(FlaskForm):
    full_name = StringField("Full Name", validators=[DataRequired(), Length(max=120)])
    staff_number = StringField(
        "Staff Number",
        validators=[Optional(), Length(min=8, max=8), Regexp(r"^\d{8}$", message="Staff number must be exactly 8 digits.")],
    )
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=120)])
    role = SelectField("Role", choices=ROLE_CHOICES, validators=[DataRequired()])
    assigned_lab_id = SelectField("Assigned Lab", coerce=int, validators=[Optional()])
    active = BooleanField("Active", default=True)
    submit = SubmitField("Create User")
