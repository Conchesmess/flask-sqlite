
# This file defines forms for the app.
# Forms let users enter information, like stories or profile details.

from flask_wtf import FlaskForm  # Main form class
from wtforms import StringField, SubmitField, TextAreaField, EmailField, HiddenField, SelectField  # Form fields
from wtforms.validators import InputRequired  # Validator for required fields
# Other validators can be used for more checks

# Form for creating/editing a story
class StoryForm(FlaskForm):
    title = StringField()  # Title of the story
    content = TextAreaField()  # Story content
    submit = SubmitField()  # Submit button

# Form for editing user profile
class ProfileForm(FlaskForm):
    fname = StringField()  # First name
    lname = StringField()  # Last name
    email_ousd = EmailField()  # School email
    email_personal = EmailField()  # Personal email
    mobile = StringField()  # Mobile number
    submit = SubmitField()  # Submit button

# Form for uploading a profile image
class ProfileImageForm(FlaskForm):
    image_url = StringField()  # URL of the image
    submit = SubmitField()  # Submit button

