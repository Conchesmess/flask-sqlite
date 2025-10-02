from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, EmailField, HiddenField, SelectField
from wtforms.validators import InputRequired
#from wtforms.validators import Length, URL, NumberRange, Email, Optional, InputRequired, ValidationError, DataRequired


class StoryForm(FlaskForm):
    title = StringField()
    content = TextAreaField()
    submit = SubmitField()

class ProfileForm(FlaskForm):
    fname = StringField()
    lname = StringField()
    email_ousd = EmailField()
    email_personal = EmailField()
    mobile = StringField()
    submit = SubmitField()

class ProfileImageForm(FlaskForm):
    image_url = StringField()
    submit = SubmitField()

class SimpleForm(FlaskForm):
    field = TextAreaField(validators=[InputRequired()])
    submit = SubmitField("Submit")

class SortOrderCohortForm(FlaskForm):
    sortOrderCohort = SelectField("Sort Value:",choices=[],validate_choice=False)
    gid = HiddenField()
    gmail = HiddenField()
    gclassid = HiddenField()
    order = HiddenField()
    submit = SubmitField("Submit")