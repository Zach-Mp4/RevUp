from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, PasswordField, DateTimeLocalField
from wtforms.validators import DataRequired, Email, Length


class UserAddForm(FlaskForm):
    """Form for adding users."""

    username = StringField('Username', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    location = StringField('Location (Optional, Can add this later.)')
    password = PasswordField('Password', validators=[Length(min=6)])

class LoginForm(FlaskForm):
    """Form for logging in users."""

    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])

class NewMeetForm(FlaskForm):
    """Form for adding a new meet"""

    title = StringField('Title', validators=[DataRequired()])
    description = StringField('Description', validators=[DataRequired()])
    location = StringField('Location (Address)', validators=[DataRequired()])
    date = DateTimeLocalField('Date and Time', validators=[DataRequired()])

class NewCarForm(FlaskForm):
    """Form for adding a car"""
    years = [str(year) for year in range(1984, 2024)]

    year = SelectField('Year', choices=[(year, year) for year in years], validators=[DataRequired()])
    make = StringField('Make', validators=[DataRequired()])
    model = StringField('Model', validators=[DataRequired()])

class SelectRangeForm(FlaskForm):
    """Select a range to search for meets"""
    options = [25, 50, 75, 100, 150, 200, 500, "All Meets"]

    range = SelectField('Range (Mi)', choices=[(option, option) for option in options],validators=[DataRequired()])

class PasswordForm(FlaskForm):
    """A form used for password verification"""

    password = PasswordField('Enter Your Password to Confirm', validators=[DataRequired()])