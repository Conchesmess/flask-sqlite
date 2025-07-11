from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField

class StoryForm(FlaskForm):
    title = StringField()
    content = TextAreaField()
    submit = SubmitField()
