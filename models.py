from flask_sqlalchemy import SQLAlchemy
from forms import *

db = SQLAlchemy()

# Models.
#----------------------------------------------------------------------------#

#can"t add to parents if it hasn't been created yet
class Genre(db.Model):
  __tablename__ = 'Genre'

  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(120), nullable=False)
 
artist_genres = db.Table('artist_genres', 
                  db.Column('genre_id', db.Integer, db.ForeignKey('Genre.id'), primary_key=True),
                  db.Column('artist_id', db.Integer, db.ForeignKey('Artist.id'), primary_key=True)
)

venue_genres = db.Table('venue_genres', 
                  db.Column('genre_id', db.Integer, db.ForeignKey('Genre.id'), primary_key=True),
                  db.Column('venue_id', db.Integer, db.ForeignKey('Venue.id'), primary_key=True)
)


class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(120))
    website = db.Column(db.String(120))
     #venue has a one to one relationship with show, venue is parent
    shows = db.relationship('Show', backref='venue', lazy=True)
    #venue has a many to many relationship with genre, venue is the parnet
    genres = db.relationship('Genre', secondary=venue_genres, backref=db.backref('venues'))

    def __repr__(self):
        return f'<Venue {self.id} {self.name}>'
    # TODO: implement any missing fields, as a database migration using Flask-Migrate


class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.relationship('Genre', secondary=artist_genres, backref=db.backref('artists'))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(120))
    shows = db.relationship('Show', backref='artist', lazy=True)

    def __repr__(self):
        return f'<Artist {self.id} {self.name}>'

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Show(db.Model):
  __tablename__ = 'Show'

  id = db.Column(db.Integer, primary_key=True)
  start_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
  venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
  artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
  
  def __repr__(self):
        return f'<Show {self.id} {self.start_time} artist_id={self.artist_id} venue_id={self.venue_id}>'

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
