"""Movie Ratings."""

from jinja2 import StrictUndefined

from flask import Flask, render_template, redirect, request, flash, session
from flask_debugtoolbar import DebugToolbarExtension

from model import User, Rating, Movie, connect_to_db, db


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Normally, if you use an undefined variable in Jinja2, it fails silently.
# This is horrible. Fix this so that, instead, it raises an error.
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
    """Homepage."""

    return render_template("homepage.html")

@app.route('/users')
def user_list():
    """Show a list of all users."""

    users = User.query.all()
    return render_template("user_list.html", users=users)

@app.route('/movies')
def movie_list():
    """Show a list of all movies."""

    movies = Movie.query.order_by(Movie.title).all()
    return render_template("movie_list.html", movies=movies)

@app.route('/users/<int:user_id>')
def user_profile(user_id):

    user = User.query.filter_by(user_id=int(user_id)).one()

    age = user.age
    zipcode = user.zipcode
    ratings = user.ratings

    return render_template("user_profile.html", user_id=user_id,
                                                age=age, 
                                                zipcode=zipcode,
                                                ratings=ratings)

@app.route('/login')
def login_page():
    """ Page where users will log in. """

    return render_template("login.html")

@app.route('/login-success', methods=['POST'])
def login_success():

    session['email'] = request.form.get("email")
    session['password'] = request.form.get("password")

    flash("Successfully logged in!")
    # somehow add form data to session
    return redirect('/') # redirect to homepage

@app.route('/logout')
def logout():

    session['email'] = None
    session['password'] = None

    flash("Successfully logged out!")

    return redirect('/')

if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the point
    # that we invoke the DebugToolbarExtension
    app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run()