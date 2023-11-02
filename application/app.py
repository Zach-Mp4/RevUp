from operator import and_, or_
import os

from flask import Flask, jsonify, render_template, request, flash, redirect, session, g
from sqlalchemy.exc import IntegrityError
from forms import NewCarForm, UserAddForm, LoginForm, NewMeetForm
from models import db, connect_db, User, Rsvp, Car, Meet
from keys import mapkey, carkey
import requests

CURR_USER_KEY = "curr_user"
MAX_ITEMS = 50

app = Flask(__name__)

# Get DB_URI from environ variable (useful for production/testing) or,
# if not set there, use development local db.
app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL', 'postgresql:///revup'))

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
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
        meets = Meet.query.limit(MAX_ITEMS).all()
        return render_template('home.html', meets = meets)
    

########################
#meets routes

@app.route('/meets/new', methods=['GET', 'POST'])
def new_meet():
    form = NewMeetForm()
    if not g.user:
        flash('Please Login', 'danger')
        return redirect('/login')
    
    if form.validate_on_submit():
        newmeet = Meet(
            creator_id = g.user.id,
            title = form.title.data,
            description = form.description.data,
            location = form.location.data,
            date = form.date.data
        )

        db.session.add(newmeet)
        db.session.commit()
        return redirect('/')
    
    return render_template('new-meet.html', form = form)

@app.route('/meets/<id>')
def show_meet(id):
    meet = Meet.query.get_or_404(id)
    if not g.user:
        flash('Please Login', 'danger')
        return redirect('/login')
    change_map(meet.location)
    return render_template('meet.html', meet = meet, rsvps = meet.rsvps)


####################
#users routes
@app.route('/users/<id>')
def show_user(id):
    user = User.query.get_or_404(id)
    if not g.user:
        flash('Please Login', 'danger')
        return redirect('/login')
    return render_template('user.html', user = user)


####################
#cars routes

@app.route('/cars/add', methods=['GET', 'POST'])
def add_car():
    form = NewCarForm()
    if not g.user:
        flash('Please Login', 'danger')
        return redirect('/login')
    
    if form.validate_on_submit():
        year = form.year.data
        make = form.make.data.lower()
        model = form.model.data.lower()
        car = Car.query.filter(Car.year == year, Car.make == make, Car.model == model).first()
        if not car:
            newcar = Car(year = year, make = make, model = model)
            db.session.add(newcar)
            db.session.commit()
            g.user.cars.append(newcar)
            db.session.commit()
            return redirect(f'/users/{g.user.id}')
        else:
            g.user.cars.append(car)
            db.session.commit()
            return redirect(f'/users/{g.user.id}')

    
    return render_template('new-car.html', form = form)

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
    return jsonify(display_strings)

@app.route('/api/addresses/<address>')
def get_addresses(address):
    URL = 'https://www.mapquestapi.com/search/v3/prediction'
    params = {
        'key': mapkey,
        'countryCode': 'US',
        'q': address,
        'collection': 'address',
        'limit': 5
    }
    resp = requests.get(URL, params = params)
    json = resp.json()
    display_strings = [result["displayString"] for result in json["results"]]
    return jsonify(display_strings)

@app.route('/api/rsvp/<meet_id>', methods=["POST"])
def rsvp(meet_id):
    if not g.user:
        flash('Please Login', 'danger')
        return redirect('/login')
    
    meet = Meet.query.get_or_404(meet_id)
    if meet not in g.user.rsvpd_meets:
        data = request.get_json()
        car_id = data.get('carid')
        if not car_id:
            rsvp = Rsvp(user_id = g.user.id, meet_id = meet.id)
            db.session.add(rsvp)
            db.session.commit()
        else:
            rsvp = Rsvp(user_id = g.user.id, meet_id = meet.id, car_id = car_id)
            db.session.add(rsvp)
            db.session.commit()
        return jsonify({
            'action': 'rsvpd'
        })
    else:
        g.user.rsvpd_meets.remove(meet)
        db.session.commit()
        return jsonify({
            'action': 'did not rsvp'
        })
    
@app.route('/api/cars/get_cars')
def get_cars():
    if not g.user:
        flash('Please Login', 'danger')
        return redirect('/login')
    
    cars = [car.json() for car in g.user.cars]
    if cars:     
        return jsonify(cars)
    else:
        return 'None'

    

#########################
# Other Functions

def change_map(address):
    URL = 'https://www.mapquestapi.com/staticmap/v5/map'
    params = {
        'key': mapkey,
        'center': address,
        'zoom': 13,
        'locations': address
    }

    resp = requests.get(URL, params = params)
    content = resp.content

    local_image_path = 'static/images/map.jpeg'

    with open(local_image_path, 'wb') as local_image_file:
        local_image_file.write(content)
    
    return '<200> OK'
    


