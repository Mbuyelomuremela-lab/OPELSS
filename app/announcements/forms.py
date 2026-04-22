from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, DateField, SubmitField
from wtforms.validators import DataRequired, Length


class AnnouncementForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired(), Length(max=200)])
    message = TextAreaField("Message", validators=[DataRequired(), Length(max=1000)])
    expiry_date = DateField("Expiry Date", validators=[DataRequired()])
    poster = FileField("Poster (optional)", validators=[FileAllowed(["jpg", "jpeg", "png", "gif", "webp"], "Images only.")])
    submit = SubmitField("Publish Announcement")
