from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length


class AssetForm(FlaskForm):
    asset_name = StringField("Asset Name", validators=[DataRequired(), Length(max=120)])
    category = StringField("Category", validators=[DataRequired(), Length(max=100)])
    serial_number = StringField("Serial Number", validators=[DataRequired(), Length(max=120)])
    status = SelectField("Status", choices=[
        ("Working Fine", "Working Fine"),
        ("Slow", "Slow"),
        ("Urgent Repair", "Urgent Repair"),
        ("Missing/Stolen", "Missing/Stolen"),
    ], validators=[DataRequired()])
    lab_id = SelectField("Lab", coerce=int, validators=[DataRequired()])
    submit = SubmitField("Save Asset")
