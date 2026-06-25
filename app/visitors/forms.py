from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, TextAreaField, DateField, SubmitField
from wtforms.validators import DataRequired, Length, Optional, Regexp


class VisitorForm(FlaskForm):
    visitor_name = StringField("Visitor Name", validators=[DataRequired(), Length(max=120)])
    category = SelectField(
        "Category",
        choices=[
            ("UNISA Student", "UNISA Student"),
            ("Educator", "Educator"),
            ("Learner", "Learner"),
            ("Other", "Other"),
        ],
        validators=[DataRequired(), Length(max=100)],
    )
    student_number = StringField(
        "Student Number",
        validators=[
            Optional(),
            Regexp(r"^\d{8}$", message="Student number must be exactly 8 digits."),
        ],
    )
    cellphone_number = StringField(
        "Cellphone Number",
        validators=[Optional(), Length(max=20)],
    )
    purpose = TextAreaField("Purpose", validators=[DataRequired(), Length(max=400)])
    visit_date = DateField("Visit Date", validators=[DataRequired()])
    lab_id = SelectField("Lab", coerce=int, validators=[DataRequired()])
    submit = SubmitField("Log Visitor")

    def validate(self, extra_validators=None):
        if not super().validate(extra_validators):
            return False
        # UNISA students must supply a student number; everyone else a cellphone.
        if self.category.data == "UNISA Student":
            if not self.student_number.data:
                self.student_number.errors.append("Student number is required for UNISA students.")
                return False
        else:
            if not self.cellphone_number.data:
                self.cellphone_number.errors.append("Cellphone number is required.")
                return False
        return True
