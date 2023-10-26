from operator import and_, or_
import os

from flask import Flask, jsonify, render_template, request, flash, redirect, session, g
from sqlalchemy.exc import IntegrityError
from forms import UserAddForm, LoginForm, NewMeetForm
from models import db, connect_db, User, Rsvp, Car, Meet
from keys import mapkey
import requests

CURR_USER_KEY = "curr_user"

app = Flask(__name__)

# Get DB_URI from environ variable (useful for production/testing) or,
# if not set there, use development local db.
app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL', 'postgresql:///revup'))

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
# app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "it's a secret")
# toolbar = DebugToolbarExtension(app)
connect_db(app)


##############################################################################
# User signup/login/logout


@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None

def do_login(user):
    """Log in user."""

    session[CURR_USER_KEY] = user.id

def do_logout():
    """Logout user."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]
    

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = UserAddForm()

    if g.user:
        return redirect('/')

    if form.validate_on_submit():
        try:
            user = User.signup(
                username=form.username.data,
                password=form.password.data,
                email=form.email.data,
                location=form.location.data
            )
            db.session.commit()

        except IntegrityError:
            flash("Username or email already taken", 'danger')
            return render_template('signup.html', form=form)

        do_login(user)

        flash('logged in', 'success')
        return redirect("/")

    return render_template('signup.html', form = form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if g.user:
        return redirect('/')

    if form.validate_on_submit():
        user = User.authenticate(form.username.data,
                                 form.password.data)

        if user:
            do_login(user)
            flash(f"Hello, {user.username}!", "success")
            return redirect("/")

        flash("Invalid credentials.", 'danger')

    return render_template('login.html', form = form)


@app.route('/logout')
def logout():
    """Handle logout of user."""

    do_logout()
    flash('Successfully Logged Out', 'success')
    return redirect('/login')

#########################
#Homepage route(s)

@app.route('/')
def homepage():
    if not g.user:
        return render_template('home-anon.html')
    else:
        return render_template('home.html')
    

########################
#meets routes

@app.route('/meets/new', methods=['GET', 'POST'])
def new_meet():
    form = NewMeetForm()
    if not g.user:
        flash('Please Login', 'danger')
        return redirect('/login')
    
    return render_template('new-meet.html', form = form)

####################
#api routes
@app.route('/api/locations/<location>')
def get_locations(location):
    URL = 'https://www.mapquestapi.com/search/v3/prediction'
    params = {
        'key': mapkey,
        'countryCode': 'US',
        'q': location,
        'collection': 'adminArea',
        'limit': 5
    }
    resp = requests.get(URL, params = params)
    json = resp.json()
    display_strings = [result["displayString"] for result in json["results"]]
    print(display_strings)
    return jsonify(display_strings)
