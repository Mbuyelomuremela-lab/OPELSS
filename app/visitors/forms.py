from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, TextAreaField, DateField, SubmitField
from wtforms.validators import DataRequired, Length


class VisitorForm(FlaskForm):
    visitor_name = StringField("Visitor Name", validators=[DataRequired(), Length(max=120)])
    category = StringField("Category", validators=[DataRequired(), Length(max=100)])
    purpose = TextAreaField("Purpose", validators=[DataRequired(), Length(max=400)])
    visit_date = DateField("Visit Date", validators=[DataRequired()])
    lab_id = SelectField("Lab", coerce=int, validators=[DataRequired()])
    submit = SubmitField("Log Visitor")
