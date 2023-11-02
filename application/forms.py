from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, PasswordField, DateTimeLocalField
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

class NewCarForm(FlaskForm):
    """Form for adding a car"""
    years = [str(year) for year in range(1984, 2024)]

    year = SelectField('Year', choices=[(year, year) for year in years], validators=[DataRequired()])
    make = StringField('Make', validators=[DataRequired()])
    model = StringField('Model', validators=[DataRequired()])