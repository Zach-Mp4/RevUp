"""Meet View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest -q test_meet_views.py


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
                                    location="Kearney, Mo")

        db.session.commit()

        self.testmeet = Meet(creator_id = self.testuser.id, title = 'test title', description = 'test description', location = '7000 NE Barry Rd, Kansas City, MO 64157', date = '2023-11-30 18:05:00')

        db.session.add(self.testmeet)
        db.session.commit()

    def test_new_meet(self):
        """test the new meet page get and post"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            
            resp = c.get('/meets/new')

            html = resp.get_data(as_text=True)

            self.assertIn('Create a New Meet!', html)

            form_data = {
                "title": 'test meet',
                'description': 'SUPER DUPER TEST',
                'location': 'test location',
                'date': '2023-11-30 18:05:00'
            }

            resp = c.post('/meets/new', data = form_data)

            self.assertEqual(resp.status_code, 302)
            meet = Meet.query.filter(Meet.title == form_data['title']).one()

            self.assertEqual(form_data['title'], meet.title)
            self.assertEqual(form_data['description'], meet.description)
            self.assertEqual(form_data['location'], meet.location)
            self.assertEqual(self.testuser.id, meet.creator_id)
        
    def test_edit_meet(self):
        """test the edit meet page get and post"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            
            resp = c.get(f'/meets/{self.testmeet.id}/edit')

            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn('Edit Meet!', html)

            form_data = {
                'title': 'test2',
                'description': 'test 2',
                'location': 'test location',
                'date': '2023-11-30 18:05:00'
            }

            c.post(f'/meets/{self.testmeet.id}/edit', data=form_data)

            self.assertEqual('test2', self.testmeet.title)
            self.assertEqual('test 2', self.testmeet.description)

    def test_show_meet(self):
        """test the show meet page"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            
            resp = c.get(f"/meets/{self.testmeet.id}")

            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)

            self.assertIn('test title', html)
            self.assertIn('Created by: testuser', html)

    def test_search_meets(self):
        """test the search meets page get and post"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            new_meet = Meet(creator_id = self.testuser.id, title = 'test title2', description = 'test description2', location = '661 S Walnut St, Gardner, KS 66030-7504, United States', date = '2023-11-30 18:05:00')
            db.session.add(new_meet)
            db.session.commit()

            resp = c.get('/meets/search')

            html = resp.get_data(as_text=True)

            self.assertIn('test title', html)
            self.assertNotIn('test title2', html)

            form_data = {
                'range': 100
            }
            resp = c.post('/meets/search', data = form_data)
            html = resp.get_data(as_text=True)
            self.assertIn('test title', html)
            self.assertIn('test title2', html)
        
    def test_delete_meet(self):
        """test delete a meet"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            
            resp = c.get(f'/meets/{self.testmeet.id}/delete')

            meets = Meet.query.all()

            self.assertNotIn(self.testmeet, meets)
            self.assertEqual(resp.status_code, 302)
            




            

