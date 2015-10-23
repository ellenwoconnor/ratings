"""Models and database functions for Ratings project."""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import correlation

# This is the connection to the SQLite database; we're getting this through
# the Flask-SQLAlchemy helper library. On this, we can find the `session`
# object, where we do most of our interactions (like committing, etc.)

db = SQLAlchemy()


##############################################################################
# Model definitions

class User(db.Model):
    """User of ratings website."""

    __tablename__ = "users"

    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    email = db.Column(db.String(64), nullable=True)
    password = db.Column(db.String(64), nullable=True)
    age = db.Column(db.Integer, nullable=True)
    zipcode = db.Column(db.String(15), nullable=True)

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<User user_id={} email={} age={} zipcode={}>".format(self.user_id, self.email, self.age, self.zipcode)

    def similarity(self, another_user):
        """Return Pearson rating for another user, as compared to self."""

        my_ratings = {}
        paired_ratings = []

        for rating in self.ratings:
            my_ratings[rating.movie_id] = rating

        for other_rating in another_user.ratings:
            my_rating = my_ratings.get(other_rating.movie_id)
            if my_rating:
                paired_ratings.append( (my_rating.score, 
                                        other_rating.score) )

        if paired_ratings:
            return correlation.pearson(paired_ratings)

        else:
            return 0.0

    def predict_rating(self, movie_id):
        """ Make a prediction for user's rating of the movie. """

        # Get all of the ratings objects for this movie ID 
        all_ratings = movie_id.ratings
        # Find all of the user objects for users who rated this movie 
        all_users = [ rating.user for rating in all_ratings ]

        # Calculate my similarity to all of the other users who rated this movie
        similarities = [
            (self.similarity(other_user), other_user)
            for other_user in all_users]

        # Sort the list of tuples by similarity score, so that the best matching users are 
        # at the top of the list. 
        # Then, get all of the best matches to us. 
        similarities.sort(reverse=True)
        top_match = similarities[0]
        other_top_matches = [element[1].user_id for element in similarities if element[0] == top_match[0]]
        highest_similarity = top_match[0]

        # print "\n"
        # print "\n"
        # print similarities
        # print "\n"
        # print "\n"
        # print "Similarities[0]: ", top_match
        # print "Top match user: ", top_match_user
        # print "Top similarity: ", highest_similarity

        rating_list = []

        for rating in all_ratings:
            if rating.user_id in other_top_matches:
                rating_list.append(rating.score)

        return (sum(rating_list) / float(len(rating_list))) * highest_similarity

# Put your Movie and Rating model classes here.

class Rating(db.Model):
    """Individual ratings on ratings website."""

    __tablename__ = "ratings"

    rating_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    movie_id = db.Column(db.Integer, db.ForeignKey('movies.movie_id'), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=True)

    user = db.relationship("User", backref=db.backref("ratings", order_by=rating_id))

    movie = db.relationship("Movie", backref=db.backref("ratings", order_by=rating_id))

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<Ratings rating_id={} user_id={} movie_id={} score={}>".format(self.rating_id, self.user_id, self.movie_id, self.score)

class Movie(db.Model):
    """Individual ratings on ratings website."""

    __tablename__ = "movies"

    movie_id = db.Column(db.Integer, nullable=False, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    released_at = db.Column(db.DateTime, nullable=False)
    imdb_url = db.Column(db.String(200), nullable=True)


    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<Movie movie_id={} title={} released_at={}>".format(self.movie_id, self.title, self.released_at)



##############################################################################
# Helper functions



def connect_to_db(app):
    """Connect the database to our Flask app."""

    # Configure to use our SQLite database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ratings.db'
    db.app = app
    db.init_app(app)


if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will leave
    # you in a state of being able to work with the database directly.

    from server import app
    connect_to_db(app)
    print "Connected to DB."
