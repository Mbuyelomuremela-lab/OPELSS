from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, IntegerField, DateField, TimeField, SelectField, SelectMultipleField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange


class ProgrammeForm(FlaskForm):
    title = StringField("Programme Title", validators=[DataRequired(), Length(max=200)])
    objective = TextAreaField("Objective", validators=[DataRequired(), Length(max=500)])
    target_audience = StringField("Target Audience", validators=[DataRequired(), Length(max=200)])
    attendance_count = IntegerField("Attendance Count", validators=[DataRequired(), NumberRange(min=0)])
    activities_done = TextAreaField("Activities Done", validators=[DataRequired(), Length(max=500)])
    date = DateField("Date", validators=[DataRequired()])
    start_time = TimeField("Start Time", format=["%H:%M", "%H:%M:%S"], validators=[DataRequired()])
    end_time = TimeField("End Time", format=["%H:%M", "%H:%M:%S"], validators=[DataRequired()])
    lab_id = SelectField("Lab", coerce=int, validators=[DataRequired()])
    facilitators = SelectMultipleField(
        "Facilitated By", coerce=int, validators=[DataRequired(message="Select at least one facilitator.")]
    )
    submit = SubmitField("Log Programme")
