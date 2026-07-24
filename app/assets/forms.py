from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, Optional


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


# Statuses that describe a problem with the asset. The fault description box is
# shown for any of these; it is mandatory only for "Urgent Repair".
PROBLEM_STATUSES = ["Slow", "Urgent Repair", "Missing/Stolen"]
DESCRIPTION_REQUIRED_STATUSES = ["Urgent Repair"]


class AssetForm(FlaskForm):
    asset_name = StringField(
        "Asset Name",
        validators=[DataRequired(), Length(max=120)],
        render_kw={"placeholder": "e.g. Dell Latitude laptop"},
    )
    category = SelectField("Category", choices=ASSET_CATEGORIES, validators=[DataRequired()])
    serial_number = StringField(
        "Unisa Tag Number",
        validators=[DataRequired(), Length(max=120)],
        render_kw={"placeholder": "e.g. LTA2100506"},
    )
    status = SelectField("Status", choices=[
        ("Working Fine", "Working Fine"),
        ("Slow", "Slow"),
        ("Urgent Repair", "Urgent Repair"),
        ("Missing/Stolen", "Missing/Stolen"),
    ], validators=[DataRequired()])
    fault_description = TextAreaField(
        "Fault Description",
        validators=[Optional(), Length(max=1000)],
    )
    lab_id = SelectField("Lab", coerce=int, validators=[DataRequired()])
    submit = SubmitField("Save Asset")

    def validate(self, extra_validators=None):
        # Run the normal field validators first. The conditional "required" rule
        # lives here rather than in an inline validator because Optional() raises
        # StopValidation on an empty field, which would skip an inline check.
        valid = super().validate(extra_validators=extra_validators)
        if self.status.data in DESCRIPTION_REQUIRED_STATUSES and not (self.fault_description.data or "").strip():
            self.fault_description.errors.append(
                "Please describe the fault when the status is Urgent Repair."
            )
            valid = False
        return valid
