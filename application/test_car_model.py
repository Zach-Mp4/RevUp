"""Car Model Tests"""

# run these tests like:
#
#    python -m unittest -q test_car_model.py


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

class CarModelTestCase(TestCase):
    """Test model for Car."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Car.query.delete()
        Meet.query.delete()

        self.client = app.test_client()

    def test_json(self):
        """test the json function"""

        car = Car(make = 'test', model = 'test_model', year = 2761)
        db.session.add(car)
        db.session.commit()

        self.assertEqual(car.json(), {
            'id': car.id,
            'make': 'test',
            'model': 'test_model',
            'year': 2761
        })
    
    def test_users(self):
        """test users relationship"""

        u = u1 = User.signup(email="test@test1.com",
            username="testuser",
            password="HASHED_PASSWORD",
            location= None)

        car = Car(make = 'test', model = 'test_model', year = 2761)
        db.session.add(car)
        db.session.commit()

        car.users.append(u)

        self.assertIsInstance(car.users[0], User)

    

