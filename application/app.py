from operator import and_, or_
import os
from flask import Flask, jsonify, render_template, request, flash, redirect, session, g
from sqlalchemy.exc import IntegrityError
from forms import NewCarForm, UserAddForm, LoginForm, NewMeetForm, SelectRangeForm, PasswordForm
from models import db, connect_db, User, Rsvp, Car, Meet
import requests
from datetime import datetime

CURR_USER_KEY = "curr_user"
mapkey = os.environ.get('mapkey')
app = Flask(__name__)

# Get DB_URI from environ variable (useful for production/testing) or,
# if not set there, use development local db.
app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL', 'postgresql:///revup'))

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "it's a secret")
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
    """show a form to signup if user not logged in and handle the submission of the form"""
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
        
        except:
            flash('Signup Error Please try again!', 'danger')
            return render_template('signup.html', form = form)

        do_login(user)

        flash('logged in', 'success')
        return redirect("/")

    return render_template('signup.html', form = form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """show a form to login if user is not logged in and handle the submission of the form"""
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
    """show the homepage to the user"""
    if not g.user:
        return render_template('home-anon.html')
    else:
        meets = ''
        if g.user.location:
            meets = get_meets_in_range(50)
        else:
            meets = Meet.query.all()
        return render_template('home.html', meets = meets)
    

########################
#meets routes

@app.route('/meets/new', methods=['GET', 'POST'])
def new_meet():
    """show a form to add a new meet and handle the submission"""
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

@app.route('/meets/<id>/edit', methods=['GET', 'POST'])
def edit_meet(id):
    if not g.user:
        flash('Please Login', 'danger')
        return redirect('/login')
    meet = Meet.query.get_or_404(id)
    if meet.creator.id == g.user.id:
        form = NewMeetForm(obj = meet)
        if form.validate_on_submit():
            meet.title = form.title.data
            meet.description = form.description.data
            meet.location = form.location.data
            meet.date = form.date.data

            db.session.add(meet)
            db.session.commit()
            return redirect(f'/meets/{meet.id}')
        return render_template('edit-meet.html', form = form)
    else:
        flash("You don't have permission to do that.", 'danger')
        return redirect('/')

@app.route('/meets/<id>')
def show_meet(id):
    """show a meets info"""
    meet = Meet.query.get_or_404(id)
    if not g.user:
        flash('Please Login', 'danger')
        return redirect('/login')
    change_map(meet.location)
    return render_template('meet.html', meet = meet, rsvps = meet.rsvps)

@app.route('/meets/search', methods=['GET', 'POST'])
def show_meets_in_range():
    """show a page to search for meets and handle the submission of the range select"""
    if not g.user:
        flash('Please Login', 'danger')
        return redirect('/login')
    
    if not g.user.location:
        flash('Please add a location to search for meets in your area!', 'danger')
        return redirect(f'/users/{g.user.id}')
    form = SelectRangeForm()

    if form.validate_on_submit():
        meets = ""
        try:
            meets = get_meets_in_range(float(form.range.data))
        except:
            meets = Meet.query.all()
        return render_template('meets.html', meets = meets, form = form)

    
    meets = get_meets_in_range(25)
    return render_template('meets.html', meets = meets, form = form)

@app.route('/meets/<id>/delete')
def delete_meet(id):
    if not g.user:
        flash('Please Login', 'danger')
        return redirect('/login')
    meet = Meet.query.get_or_404(id)
    if g.user.id == meet.creator.id:
        Meet.query.filter(Meet.id == meet.id).delete()
        db.session.commit()
        flash('Meet Deleted Successfully.', 'success')
        return redirect(f'/users/{g.user.id}')
    else:
        flash("You don't have permission to do that.", 'danger')
        return redirect(f'/meets/{id}')

####################
#users routes
@app.route('/users/<id>')
def show_user(id):
    """show a users info"""
    user = User.query.get_or_404(id)
    if not g.user:
        flash('Please Login', 'danger')
        return redirect('/login')
    return render_template('user.html', user = user)

@app.route('/users/edit', methods=['GET', 'POST'])
def edit_user():
    if not g.user:
        flash('Please Login', 'danger')
        return redirect('/login')
    user = User.query.get_or_404(session[CURR_USER_KEY])
    form = UserAddForm(obj = user)

    if form.validate_on_submit():
        password = form.password.data
        user = User.authenticate(user.username, password)
        if user:
            user.username = form.username.data
            user.email = form.email.data
            user.location = form.location.data
            db.session.add(user)
            db.session.commit()
            flash('Successfully edited profile!', 'success')
            return redirect(f'/users/{user.id}')

    return render_template('edit-user.html', form = form)

@app.route('/users/delete', methods=['GET', 'POST'])
def delete_user():
    if not g.user:
        flash('Please Login', 'danger')
        return redirect('/login')
    form = PasswordForm()
    if form.validate_on_submit():
        user = User.authenticate(g.user.username, form.password.data)
        if user:
            do_logout()
            User.query.filter(User.id == user.id).delete()
            flash('Account Deleted Successfully.', 'success')
            return redirect('/')
        else:
            flash('Incorrect Password', 'danger')
            return redirect('/users/delete')
    return render_template('delete-user.html', form = form)
    
####################
#cars routes

@app.route('/cars/add', methods=['GET', 'POST'])
def add_car():
    """show a form for a user to add a car to their garage and handle the submission"""
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
    """return a list of 5 locations based on what the user has typed in so far"""
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
    """return a list of 5 addresses based on what the user has typed in so far"""
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
    """rsvp a user if they are not rsvpd and un-rsvp if they are rsvpd"""
    if not g.user:
        flash('Please Login', 'danger')
        return redirect('/login')
    
    meet = Meet.query.get_or_404(meet_id)
    if meet not in g.user.rsvpd_meets:
        try:
            data = request.get_json()
            car_id = data.get('carid')
            rsvp = Rsvp(user_id = g.user.id, meet_id = meet.id, car_id = car_id)
            db.session.add(rsvp)
            db.session.commit()
        except:
            rsvp = Rsvp(user_id = g.user.id, meet_id = meet.id)
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
    """return a list of a users cars"""
    if not g.user:
        flash('Please Login', 'danger')
        return redirect('/login')
    
    cars = [car.json() for car in g.user.cars]
    if cars:     
        return jsonify(cars)
    else:
        return 'None'

@app.route('/api/cars/delete/<id>', methods=['DELETE'])
def remove_car(id):
    if not g.user:
        flash('Please Login', 'danger')
        return redirect('/login')
    
    car = Car.query.get_or_404(id)

    try:
        g.user.cars.remove(car)
        db.session.commit()
        return jsonify({
            'result': 'success'
        })
    except:
        return jsonify({
            'result': 'failed'
        })


#########################
# Other Functions

def change_map(address):
    """change the map image file to the being viewed map"""
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

def get_meets_in_range(range):
    """get meets within a users specified range"""
    URL = 'https://www.mapquestapi.com/directions/v2/route'
    meets = Meet.query.all()
    locations = [meet.location for meet in meets]

    distances = []

    counter = 0
    try:
        for location in locations:
            params = {
            'key': mapkey,
            'from': g.user.location,
            'to': location
        }
            resp = requests.get(URL, params = params)
            data = resp.json()
            distance = (data['route']['distance'], locations[counter])
            distances.append(distance)
            counter += 1
    except:
        return Meet.query.all()


    filter = [distance[1] for distance in distances if distance[0] <= range]
    today_datetime = datetime.now()
    final_meets = [meet for meet in meets if meet.location in filter and meet.date > today_datetime]
    return final_meets

