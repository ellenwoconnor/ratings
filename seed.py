"""Utility file to seed ratings database from MovieLens data in seed_data/"""


from model import User
# from model import Rating
from model import Rating
# from model import Movie
from model import Movie

from datetime import datetime
from model import connect_to_db, db
from server import app


def load_users():
    """Load users from u.user into database."""

    print "Users"

    # Delete all rows in table, so if we need to run this a second time,
    # we won't be trying to add duplicate users
    User.query.delete()

    # Read u.user file and insert data
    for row in open("seed_data/u.user"):
        row = row.rstrip()
        user_id, age, gender, occupation, zipcode = row.split("|")

        user = User(user_id=user_id,
                    age=age,
                    zipcode=zipcode)

        # We need to add to the session or it won't ever be stored
        db.session.add(user)

    # Once we're done, we should commit our work
    db.session.commit()


def load_movies():
    """Load movies from u.item into database."""

    print "Movies"

    Movie.query.delete()

    for row in open("seed_data/u.item"):
        row = row.rstrip()
        split_row = row.split("|")

        movie_id = split_row[0]
        title = split_row[1]
        released_at = split_row[2]
        imdb_url = split_row[4]

        title = title.rstrip("()1234567890")
        title = title.rstrip()

        if len(released_at) == 11:
            released_at = datetime.strptime(released_at, "%d-%b-%Y")

        if title != "unknown":
            movie = Movie(movie_id=movie_id,
                            title=title,
                            released_at=released_at,
                            imdb_url=imdb_url)

            db.session.add(movie)

    db.session.commit()



def load_ratings():
    """Load ratings from u.data into database."""

    print "Ratings"

    Rating.query.delete()

    for row in open('seed_data/u.data'):
        row = row.rstrip()

        user_id, movie_id, score, timestamp = row.split()
        timestamp = datetime.fromtimestamp(float(timestamp))

### TODO
### This is not working!
### We're trying to check if the movie referenced by a rating exists.

        # check_movie = Movie.query.filter_by(movie_id=movie_id).count()
        # if check_movie != 0:

        rating = Rating(user_id=user_id, movie_id=movie_id, score=score, 
                        timestamp=timestamp)

        db.session.add(rating)

    db.session.commit()


### Potential solution, not working

# def clean_data():
#     bad_data = db.session.query(Rating).filter(Rating.movie.movie_id is NULL).all()

if __name__ == "__main__":
    connect_to_db(app)

    # In case tables haven't been created, create them
    db.create_all()

    # Import different types of data
    load_users()
    load_movies()
    load_ratings()
