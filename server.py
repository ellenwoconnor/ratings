"""Movie Ratings."""

from jinja2 import StrictUndefined

from flask import Flask, render_template, redirect, request, flash, session
from flask_debugtoolbar import DebugToolbarExtension

from model import User, Rating, Movie, connect_to_db, db
from datetime import datetime

### TODO: Fix login so it'll only work if you have an account.
######### Otherwise, it should flash a message saying the login details are incorrect.


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Normally, if you use an undefined variable in Jinja2, it fails silently.
# This is horrible. Fix this so that, instead, it raises an error.
app.jinja_env.undefined = StrictUndefined

@app.route('/')
def index():

    if 'email' not in session:
        session['email'] = None
    if 'password' not in session:
        session['password'] = None

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
    """Show information about a user."""
    user = User.query.filter_by(user_id=int(user_id)).one()

    age = user.age
    zipcode = user.zipcode
    ratings = user.ratings

    return render_template("user_profile.html", user_id=user_id,
                                                age=age, 
                                                zipcode=zipcode,
                                                ratings=ratings)

@app.route('/movies/<int:movie_id>')
def movie_profile(movie_id):
    """Show information about a movie."""
    movie = Movie.query.filter_by(movie_id=int(movie_id)).one()

    title = movie.title
    released_at = movie.released_at
    imdb_url = movie.imdb_url
    ratings = movie.ratings

    return render_template("movie_profile.html", movie_id=movie_id,
                                                title=title, 
                                                imdb_url=imdb_url,
                                                released_at=released_at,
                                                ratings=ratings)

@app.route('/login')
def login_page():
    """ Page where users will log in. """

    return render_template("login.html")

@app.route('/login-success', methods=['POST'])
def login_success():
    """Log the user in and redirect them to the homepage."""

    session['email'] = request.form.get("email")
    session['password'] = request.form.get("password")

    user = db.session.query(User).filter(User.email == session['email']).first()

    if user = None:
        flash("Wrong login info!")

    elif user.email == session['email'] and user.password == session['password']:
        flash("Successfully logged in!")

    else:
        flash("Wrong login info!")


    return redirect('/') # redirect to homepage

@app.route('/logout')
def logout():
    """Log the user out and redirect them to the homepage."""

    session['email'] = None
    session['password'] = None

    flash("Successfully logged out!")

    return redirect('/')

@app.route('/rating_success', methods=["POST"])
def rating_successful():
    """Process new rating and redirect to movie profile page."""

    score = request.form.get("rating")
    user_email = session["email"]
    timestamp = datetime.now()
    movie_id = request.form.get("movie_id")

    # Query the DB for the user id, using the email from the session
    user_id = db.session.query(User).filter(User.email == user_email).one().user_id

    count_ratings = db.session.query(Rating).filter(Rating.user_id == user_id, Rating.movie_id == movie_id).count()

    if count_ratings == 0:
        rating = Rating(user_id=user_id, movie_id=movie_id, score=score, 
                        timestamp=timestamp)

        db.session.add(rating)
        db.session.commit()

        flash("Successfully added rating!")

    elif count_ratings == 1:
        rating = db.session.query(Rating).filter(Rating.user_id == user_id, Rating.movie_id == movie_id)
        rating.score = score
        db.session.commit()

        flash("Successfully updated rating!")

    return redirect('/movies/' + movie_id)




if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the point
    # that we invoke the DebugToolbarExtension
    app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run()