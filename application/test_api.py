"""api tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest -q test_api.py


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
    
    def test_get_locations(self):
        """test the get locations api route which uses mapquest api"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            
            resp = c.get('/api/locations/kan')
            data = resp.json
            self.assertEqual(len(data), 5)

    def test_get_addresses(self):
        """test the get addresses api route which uses mapquest api"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            
            resp = c.get('/api/addresses/1323')
            data = resp.json
            self.assertEqual(len(data), 5)
    
    def test_rsvp(self):
        """test the api route which handles users rsvp"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            meet = Meet(creator_id = self.testuser.id, title = 'test title', description = 'test description', location = 'test location', date = '2023-11-30 18:05:00')
            db.session.add(meet)
            db.session.commit()

            url = f"/api/rsvp/{meet.id}"
            #rsvp
            resp = c.post(url)

            meets = self.testuser.rsvpd_meets

            self.assertIn(meet, meets)
            #un-rsvp
            resp = c.post(url)

            meets = self.testuser.rsvpd_meets

            self.assertNotIn(meet, meets)

    def test_get_cars(self):
        """test the api path which gets a users cars list"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            
            car = Car(year = 2017, make = 'test', model = 'test')

            db.session.add(car)
            db.session.commit()

            self.testuser.cars.append(car)

            db.session.commit()

            resp = c.get('/api/cars/get_cars')

            data = resp.json

            self.assertEqual(len(data), 1)
    
    def test_delete_car(self):
         with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            
            car = Car(year = 2017, make = 'test', model = 'test')

            db.session.add(car)
            db.session.commit()

            self.testuser.cars.append(car)

            db.session.commit()

            resp = c.delete(f'/api/cars/delete/{car.id}')

            self.assertNotIn(car, self.testuser.cars)

