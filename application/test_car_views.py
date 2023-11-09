"""Car View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest -q test_car_views.py


import os
from unittest import TestCase
from sqlalchemy.orm.exc import NoResultFound
from models import db, connect_db, Car, User, Meet

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///revup-test"

# Now we can import app

from app import app, CURR_USER_KEY

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data
ctx = app.app_context()
ctx.push()
db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


class UserViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Car.query.delete()
        Meet.query.delete()
        self.client = app.test_client()

        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    location=None)

        db.session.commit()
    
    def test_add_car(self):
        """test the adding a car page get and post"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            
            resp = c.get('/cars/add')

            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Add a Car to Your Garage!', html)

            form_data = {
                'year': 2016,
                'make': 'scion',
                'model': 'tc'
            }

            resp = c.post('/cars/add', data=form_data)

            cars = self.testuser.cars
            car = Car.query.filter(Car.year == 2016).one()
            self.assertIn(car, cars)
            self.assertEqual(resp.status_code, 302)    