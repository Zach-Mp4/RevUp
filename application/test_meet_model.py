"""meet Model Tests"""

# run these tests like:
#
#    python -m unittest -q test_meet_model.py


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

class MeetModelTestCase(TestCase):
    """Test model for Meets."""
    
    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Car.query.delete()
        Meet.query.delete()

        self.client = app.test_client()

    def test_creator(self):
        """test creator relationship"""

        u1 = User.signup(email="test@test1.com",
            username="testuser",
            password="HASHED_PASSWORD",
            location= None)
        db.session.commit()

        meet = Meet(creator_id = u1.id, title = 'test title', description = 'test description', location = 'test location', date = '2023-11-30 18:05:00')

        db.session.add(meet)
        db.session.commit()
        
        self.assertIsInstance(meet.creator, User)
        self.assertEqual(meet.creator, u1)

    def test_rsvpd_users(self):
        """test rsvpd_users relationship"""

        u1 = User.signup(email="test@test1.com",
            username="testuser",
            password="HASHED_PASSWORD",
            location= None)
        db.session.commit()

        meet = Meet(creator_id = u1.id, title = 'test title', description = 'test description', location = 'test location', date = '2023-11-30 18:05:00')

        db.session.add(meet)
        db.session.commit()
        u2 = User.signup(email="test@test2.com",
            username="testuse2",
            password="HASHED_PASSWORD3",
            location= None)
        db.session.commit()

        meet.rsvpd_users.append(u2)

        self.assertIsInstance(meet.rsvpd_users[0], User)

    


