from flask import jsonify
from flask_bcrypt import Bcrypt
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

bcrypt = Bcrypt()
db = SQLAlchemy()

def connect_db(app):
    """Connect this database to provided Flask app.

    You should call this in your Flask app.
    """

    db.app = app
    db.init_app(app)

class User(db.Model):
    """define the User model"""

    __tablename__ = "users"

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    email = db.Column(
        db.Text,
        nullable=False,
        unique = True
    )

    username = db.Column(
        db.Text,
        nullable=False,
        unique=True
    )

    location = db.Column(
        db.Text,
        nullable=True,
        unique=False
    )

    password = db.Column(
        db.Text,
        nullable=False
    )

    cars = db.relationship(
        "Car",
        secondary='users_cars',
        backref='users'
    )

    @classmethod
    def signup(cls, username, email, password, location):
        """sign up a user and hash their password"""

        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(
            username=username,
            email=email,
            password=hashed_pwd,
            location = location
        )

        db.session.add(user)
        return user
    
    @classmethod
    def authenticate(cls, username, password):
        """Find user with `username` and `password`.

        This is a class method (call it on the class, not an individual user.)
        It searches for a user whose password hash matches this password
        and, if it finds such a user, returns that user object.

        If can't find matching user (or if password is wrong), returns False.
        """

        user = cls.query.filter_by(username=username).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user

        return False




class Car(db.Model):
    """define the Car model"""

    __tablename__ = "cars"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    make = db.Column(
        db.Text,
        unique=False,
        nullable=False
    )

    model = db.Column(
        db.Text,
        unique=False,
        nullable=False
    )

    year = db.Column(
        db.Integer,
        nullable=False,
        unique=False
    )

    def represent(self):
        return f'{self.year} {self.make} {self.model}'
    
    def json(self):
        return {
            'id': self.id,
            'year': self.year,
            'make': self.make,
            'model': self.model
        }

class User_Car(db.Model):
    """define the connection between the users and cars tables"""

    __tablename__ = "users_cars"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False
    )

    car_id = db.Column(
        db.Integer,
        db.ForeignKey('cars.id', ondelete='CASCADE')
    )

class Meet(db.Model):
    """define the meet model"""

    __tablename__ = "meets"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    creator_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False
    )

    title = db.Column(
        db.Text,
        nullable=False
    )

    description = db.Column(
        db.Text,
        nullable=False
    )

    location = db.Column(
        db.Text,
        nullable=False,
        unique=False
    )

    date = db.Column(
        db.DateTime,
        nullable=False,
        unique=False
    )

    creator = db.relationship('User', backref='created_meets')

    rsvpd_users = db.relationship(
        'User',
        secondary='rsvps',
        backref='rsvpd_meets'
        )
    
    rsvps = db.relationship('Rsvp')
    


class Rsvp(db.Model):
    """Define the rsvp model"""
    
    __tablename__ = 'rsvps'

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False
    )

    meet_id = db.Column(
        db.Integer,
        db.ForeignKey('meets.id', ondelete='CASCADE'),
        nullable=False
    )

    user = db.relationship('User')

    car_id = db.Column(
        db.Integer,
        db.ForeignKey('cars.id', ondelete='CASCADE'),
        nullable=True
    )

    car = db.relationship('Car')

