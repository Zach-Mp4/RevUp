"""User Model Tests"""

# run these tests like:
#
#    python -m unittest -q test_user_model.py


import os
from unittest import TestCase
from models import db, User, Car, Meet

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///revup-test"

from app import app
ctx = app.app_context()
ctx.push()
db.create_all()

class UserModelTestCase(TestCase):
    """Test model for Users."""
    
    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Car.query.delete()
        Meet.query.delete()

        self.client = app.test_client()
    
    def test_signup(self):
        """test if signup creates user if given proper credentials"""

        u1 = User.signup(email="test@test1.com",
            username="testuser",
            password="HASHED_PASSWORD",
            location= None)
        db.session.commit()

        self.assertIsInstance(u1, User)

    def test_authenticate(self):
        """test the authenticate method"""

        u = u1 = User.signup(email="test@test1.com",
            username="testuser",
            password="HASHED_PASSWORD",
            location= None)
        db.session.commit()

        u_login = User.authenticate(username = 'testuser', password = "HASHED_PASSWORD")

        self.assertIsInstance(u_login, User)

        u_fail_username = User.authenticate(username = 'testuser1', password = 'HASHED_PASSWORD')

        self.assertFalse(u_fail_username)

        u_fail_password = User.authenticate(username = 'testuser', password = 'HASHED_PASSWORD11')

        self.assertFalse(u_fail_username)

    def test_cars(self):
        """test if a users car relationship is working"""

        u = u1 = User.signup(email="test@test1.com",
            username="testuser",
            password="HASHED_PASSWORD",
            location= None)
        db.session.commit()

        car = Car(make = 'test_make', model = 'test_model', year = 2016)

        u.cars.append(car)

        db.session.commit()
        
        self.assertIsInstance(u.cars[0], Car)

    def test_rsvpd_meets(self):
        """test if a users rsvpd meets relationship is working"""
        u = u1 = User.signup(email="test@test1.com",
            username="testuser",
            password="HASHED_PASSWORD",
            location= None)
        db.session.commit()

        meet = Meet(creator_id = u.id, title = 'test title', description = 'test description', location = 'test location', date = '2023-11-30 18:05:00')

        u.rsvpd_meets.append(meet)
        db.session.commit()

        self.assertIsInstance(u.rsvpd_meets[0], Meet)

    def test_created_meets(self):
        """test if a users rsvpd meets relationship is working"""
        u = u1 = User.signup(email="test@test1.com",
            username="testuser",
            password="HASHED_PASSWORD",
            location= None)
        db.session.commit()

        meet = Meet(creator_id = u.id, title = 'test title', description = 'test description', location = 'test location', date = '2023-11-30 18:05:00')

        u.rsvpd_meets.append(meet)
        db.session.commit()

        self.assertIsInstance(u.created_meets[0], Meet)

    
    
