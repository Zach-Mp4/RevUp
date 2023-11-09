"""User View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest -q test_user_views.py


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

    def test_show_user(self):
         """test the user page"""
         with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.get(f'/users/{self.testuser.id}')

            html = resp.get_data(as_text=True)

            self.assertIn('testuser', html)

            meet = Meet(creator_id = self.testuser.id, title = 'test title', description = 'test description', location = 'test location', date = '2023-11-30 18:05:00')

            db.session.add(meet)
            db.session.commit()

            resp = c.get(f'/users/{self.testuser.id}')

            html = resp.get_data(as_text=True)

            self.assertIn('testuser', html)
            self.assertIn('test title', html)

    def test_edit_user(self):
        """test the edit user view get and post"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            
            resp = c.get(f'/users/edit')

            html = resp.get_data(as_text=True)

            self.assertIn('Edit Your Profile!', html)

            form_data = {
                'username': 'testuser55',
                 'email': "test55@test.com",
                 'location': "Kearney, MO, USA",
                 'password': 'testuser'
            }
            resp = c.post(f'/users/edit', data=form_data)

            self.assertEqual(self.testuser.username, 'testuser55')
            self.assertEqual(self.testuser.email, 'test55@test.com')
            self.assertEqual(self.testuser.location, 'Kearney, MO, USA')
            self.assertEqual(resp.status_code, 302)
    
    def test_delete_user(self):
        """test the delete account page get and post"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            
            resp = c.get('/users/delete')

            html = resp.get_data(as_text=True)

            self.assertIn('Delete Account?', html)

            form_data = {
                 'password': 'testuser'
            }

            resp = c.post('/users/delete', data=form_data)

            self.assertEqual(resp.status_code, 302)

            all_users = User.query.all()

            self.assertNotIn(self.testuser, all_users)

        
    