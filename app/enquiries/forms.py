from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length


class EnquiryForm(FlaskForm):
    student_name = StringField("Student Name", validators=[DataRequired(), Length(max=120)])
    student_number = StringField("Student Number", validators=[DataRequired(), Length(max=60)])
    category = StringField("Category", validators=[DataRequired(), Length(max=120)])
    description = TextAreaField("Description", validators=[DataRequired(), Length(max=500)])
    escalation_reason = TextAreaField("Reason for Escalation", validators=[DataRequired(), Length(max=400)])
    lab_id = SelectField("Lab", coerce=int, validators=[DataRequired()])
    submit = SubmitField("Submit & Escalate")


class AssignEnquiryForm(FlaskForm):
    assigned_to = SelectField("Assign To", coerce=int, validators=[DataRequired()])
    submit = SubmitField("Assign")


class ResolveEnquiryForm(FlaskForm):
    resolution_note = TextAreaField("Resolution Note", validators=[DataRequired(), Length(max=400)])
    submit = SubmitField("Mark Resolved")


class NotResolvedForm(FlaskForm):
    not_resolved_reason = TextAreaField("Reason Not Resolved", validators=[DataRequired(), Length(max=400)])
    submit = SubmitField("Mark Not Resolved")


class TrackingForm(FlaskForm):
    tracking_number = StringField("Tracking Number", validators=[DataRequired(), Length(max=30)])
    submit = SubmitField("Track Enquiry")
