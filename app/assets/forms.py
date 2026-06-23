from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length


ASSET_CATEGORIES = [
    ("Laptop/Desktop", "Laptop / Desktop"),
    ("Projector", "Projector"),
    ("Printer", "Printer"),
    ("Smartboard", "Smartboard"),
    ("Router", "Router"),
    ("Monitor", "Monitor"),
    ("UPS", "UPS"),
    ("Other", "Other"),
]


class AssetForm(FlaskForm):
    asset_name = StringField("Asset Description", validators=[DataRequired(), Length(max=120)])
    category = SelectField("Category", choices=ASSET_CATEGORIES, validators=[DataRequired()])
    serial_number = StringField("Unisa Tag Number", validators=[DataRequired(), Length(max=120)])
    status = SelectField("Status", choices=[
        ("Working Fine", "Working Fine"),
        ("Slow", "Slow"),
        ("Urgent Repair", "Urgent Repair"),
        ("Missing/Stolen", "Missing/Stolen"),
    ], validators=[DataRequired()])
    lab_id = SelectField("Lab", coerce=int, validators=[DataRequired()])
    submit = SubmitField("Save Asset")
