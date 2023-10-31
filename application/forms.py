from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, DateTimeLocalField
from wtforms.validators import DataRequired, Email, Length


class UserAddForm(FlaskForm):
    """Form for adding users."""

    username = StringField('Username', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[Length(min=6)])
    location = StringField('Location (Optional, Can add this later.)')

class LoginForm(FlaskForm):
    """Form for logging in users."""

    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[Length(min=6)])

class NewMeetForm(FlaskForm):
    """Form for adding a new meet"""

    title = StringField('Title', validators=[DataRequired()])
    description = StringField('Description', validators=[DataRequired()])
    location = StringField('Location (Address)', validators=[DataRequired()])
    date = DateTimeLocalField('Date and Time', validators=[DataRequired()])
