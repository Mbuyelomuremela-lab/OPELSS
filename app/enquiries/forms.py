from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length


class EnquiryForm(FlaskForm):
    student_name = StringField("Student Name", validators=[DataRequired(), Length(max=120)])
    student_number = StringField("Student Number", validators=[DataRequired(), Length(max=60)])
    category = StringField("Category", validators=[DataRequired(), Length(max=120)])
    description = TextAreaField("Description", validators=[DataRequired(), Length(max=500)])
    lab_id = SelectField("Lab", coerce=int, validators=[DataRequired()])
    submit = SubmitField("Submit Enquiry")


class UpdateEnquiryForm(FlaskForm):
    status = SelectField("Status", choices=[
        ("Open", "Open"),
        ("In Progress", "In Progress"),
        ("Escalated", "Escalated"),
        ("Resolved", "Resolved"),
        ("Closed", "Closed"),
    ], validators=[DataRequired()])
    resolution_note = TextAreaField("Resolution Note", validators=[Length(max=400)])
    submit = SubmitField("Update Status")


class TrackingForm(FlaskForm):
    tracking_number = StringField("Tracking Number", validators=[DataRequired(), Length(max=30)])
    submit = SubmitField("Track Enquiry")
