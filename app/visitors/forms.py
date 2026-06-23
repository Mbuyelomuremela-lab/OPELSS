from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, TextAreaField, DateField, SubmitField
from wtforms.validators import DataRequired, Length, Optional


class VisitorForm(FlaskForm):
    visitor_name = StringField("Visitor Name", validators=[DataRequired(), Length(max=120)])
    category = SelectField(
        "Category",
        choices=[
            ("Educator", "Educator"),
            ("Unisa Student", "Unisa Student"),
            ("High School Learner", "High School Learner"),
            ("Others", "Others"),
        ],
        validators=[DataRequired()],
    )
    student_number = StringField("Student Number", validators=[Optional(), Length(max=32)])
    id_number = StringField("ID Number", validators=[Optional(), Length(max=32)])
    purpose = TextAreaField("Reason for Visit", validators=[DataRequired(), Length(max=400)])
    visit_date = DateField("Visit Date", validators=[DataRequired()])
    lab_id = SelectField("Lab", coerce=int, validators=[DataRequired()])
    submit = SubmitField("Log Visitor")

    def validate(self):
        valid = super().validate()
        if not valid:
            return False

        if self.category.data == "Unisa Student":
            if not self.student_number.data:
                self.student_number.errors.append("Student number is required for Unisa Student.")
                return False
        else:
            if not self.id_number.data:
                self.id_number.errors.append("ID number is required for this category.")
                return False
        return True
