#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import re
import json
import sys
from operator import itemgetter
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from flask_migrate import Migrate
from forms import *
#----------------------------------------------------------------------------#m
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
from models import db, Venue, Artist, Genre, Show, venue_genres, artist_genres
db.init_app(app)
migrate = Migrate(app, db)

# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.                     
  venues = Venue.query.all()

  data = []
  locations = set() # tried using a [], got duplicates. sets prevent duplicates
  for venue in venues:
    locations.add((venue.state, venue.city))

  locations = list(locations) #turn set to list for sorting, the method .sort() cannot be called on a set directly
  locations.sort(key=itemgetter(1,0)) #sorts the list

  
  for city in locations:
    city_venues = []
    for venue in venues: 
      if (venue.state == city[0]) and (venue.city == city[1]):     
        show_locations = Show.query.filter_by(venue_id=venue.id).all()
        print(show_locations)
        num_upcoming = 0
        for show in show_locations:
          if show.start_time > datetime.now():
            num_upcoming += 1
        
        city_venues.append({
         "id": venue.id,
         "name": venue.name,
         "num_upcoming_shows": num_upcoming
        })
    
    data.append({
      "city": city[0],
      "state": city[1],
      "venues": city_venues
    })
  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on venues with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_term = request.form.get('search_term', '').strip()

  venues = Venue.query.filter(Venue.name.ilike('%' + search_term + '%')).all()  
  venue_list = []
  for venue in venues:
    venue_shows = Show.query.filter_by(venue_id=venue.id).all()
    num_upcoming = 0
    for show in venue_shows:

      if show.start_time > datetime.now():
        num_upcoming += 1

    venue_list.append({
      "id": venue.id,
      "name": venue.name,
      "num_upcoming_shows": num_upcoming 
    })

  response = {
      "count": len(venues),
      "data": venue_list
  }
   
  # TODO: implement search on venues with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  # # response={
  # #   "count": 1,
  # #   "data": [{
  # #     "id": 2,
  # #     "name": "The Dueling Pianos Bar",
  # #     "num_upcoming_shows": 0,
  # #   }]
  #   }
  return render_template('pages/search_venues.html', results=response, search_term=search_term)

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  venue = Venue.query.get(venue_id)
  
  #genres could be more than one
  genres = []
  for genre in venue.genres:
    genres.append(genre.name)
  
  # past_shows = []
  # past_shows_count = 0
  # upcoming_shows_count = []
  # upcoming_shows_count = 0

  # for show in venue.shows:
  #   if show.start_time > datetime.now():
  #     upcoming_shows_count += 1
  #     upcoming_shows.append({
  #       "artist_id": show.artist_id,
  #       "artist_name": show.artist.name,
  #       "artist_image_link": show.artist.image_link,
  #       "start_time": format_datetime(str(show.start_time))
  #       })
  #   else:
  #     past_shows_count += 1
  #     past_shows.append({
  #       "artist_id": show.artist_id,
  #       "artist_name": show.artist.name,
  #       "artist_image_link": show.artist.image_link,
  #       "start_time": format_datetime(str(show.start_time))
  #     })

  past_shows_query = db.session.query(Show).join(Artist).filter(Show.venue_id==venue_id).filter(Show.start_time<datetime.now()).all()   
  past_shows = []
  past_shows_count = db.session.query(Show).join(Artist).filter(Show.venue_id==venue_id).filter(Show.start_time<datetime.now()).count()
  for show in past_shows_query:
      past_shows.append({
        "artist_id": show.artist_id,
        "artist_name": show.artist.name,
        "artist_image_link": show.artist.image_link,
        "start_time": format_datetime(str(show.start_time))
      })

  upcoming_shows_query = db.session.query(Show).join(Venue).filter(Show.venue_id==venue_id).filter(Show. start_time>datetime.now()).all()   
  upcoming_shows = []
  upcoming_shows_count = db.session.query(Show).join(Venue).filter(Show.venue_id==venue_id).filter(Show. start_time>datetime.now()).count()
  for show in upcoming_shows_query:
    upcoming_shows.append({
      "artist_id": show.artist_id,
      "artist_name": show.artist.name,
      "artist_image_link": show.artist.image_link,
      "start_time": format_datetime(str(show.start_time))
    })

  data={
    "id": venue.id,
    "name": venue.name,
    "genres": genres,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": (venue.phone[:3] + '-' + venue.phone[3:6] + '-' + venue.phone[6:]), # result is 000-000-0000 or whatever numbers
    "website": venue.website,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": past_shows_count,
    "upcoming_shows_count": upcoming_shows_count,
  }
      

  # data1={
  #   "id": 1,
  #   "name": "The Musical Hop",
  #   "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
  #   "address": "1015 Folsom Street",
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "123-123-1234",
  #   "website": "https://www.themusicalhop.com",
  #   "facebook_link": "https://www.facebook.com/TheMusicalHop",
  #   "seeking_talent": True,
  #   "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
  #   "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
  #   "past_shows": [{
  #     "artist_id": 4,
  #     "artist_name": "Guns N Petals",
  #     "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
  #     "start_time": "2019-05-21T21:30:00.000Z"
  #   }],
  #   "upcoming_shows": [],
  #   "past_shows_count": 1,
  #   "upcoming_shows_count": 0,
  # }
  # data2={
  #   "id": 2,
  #   "name": "The Dueling Pianos Bar",
  #   "genres": ["Classical", "R&B", "Hip-Hop"],
  #   "address": "335 Delancey Street",
  #   "city": "New York",
  #   "state": "NY",
  #   "phone": "914-003-1132",
  #   "website": "https://www.theduelingpianos.com",
  #   "facebook_link": "https://www.facebook.com/theduelingpianos",
  #   "seeking_talent": False,
  #   "image_link": "https://images.unsplash.com/photo-1497032205916-ac775f0649ae?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=750&q=80",
  #   "past_shows": [],
  #   "upcoming_shows": [],
  #   "past_shows_count": 0,
  #   "upcoming_shows_count": 0,
  # }
  # data3={
  #   "id": 3,
  #   "name": "Park Square Live Music & Coffee",
  #   "genres": ["Rock n Roll", "Jazz", "Classical", "Folk"],
  #   "address": "34 Whiskey Moore Ave",
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "415-000-1234",
  #   "website": "https://www.parksquarelivemusicandcoffee.com",
  #   "facebook_link": "https://www.facebook.com/ParkSquareLiveMusicAndCoffee",
  #   "seeking_talent": False,
  #   "image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #   "past_shows": [{
  #     "artist_id": 5,
  #     "artist_name": "Matt Quevedo",
  #     "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
  #     "start_time": "2019-06-15T23:00:00.000Z"
  #   }],
  #   "upcoming_shows": [{
  #     "artist_id": 6,
  #     "artist_name": "The Wild Sax Band",
  #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #     "start_time": "2035-04-01T20:00:00.000Z"
  #   }, {
  #     "artist_id": 6,
  #     "artist_name": "The Wild Sax Band",
  #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #     "start_time": "2035-04-08T20:00:00.000Z"
  #   }, {
  #     "artist_id": 6,
  #     "artist_name": "The Wild Sax Band",
  #     "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #     "start_time": "2035-04-15T20:00:00.000Z"
  #   }],
  #   "past_shows_count": 1,
  #   "upcoming_shows_count": 1,
  # }
  # data = list(filter(lambda d: d['id'] == venue_id, [data1, data2, data3]))[0]
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():

  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  form = VenueForm(request.form)
  if form.seeking_talent.data == 'Yes':
    seeking_talent = True
  else:
    seeking_talent = False
  #phone number validator
  phone = form.phone.data
  validate_phone = re.compile(r'[0-9()+/s]+')

  while not validate_phone.match(phone):
    flash('phone number is not valid')
    return redirect(url_for('create_venue_submission'))

  if not form.validate():
        flash( form.errors )
        return redirect(url_for('create_venue_submission'))  
  else:
      error_in_insert = False
      phone = re.sub('\D', '',  phone)
      try:
        venue = Venue(name=form.name.data, city=form.city.data, state=form.state.data, website=form.website_link.data, 
                      address=form.address.data, phone=phone, image_link=form.image_link.data,
                      facebook_link=form.facebook_link.data, seeking_description=form.seeking_description.data,  
                      seeking_talent=seeking_talent)
    
        genres = form.genres.data
    
        for genre in genres:
          fetch_genre = Genre.query.filter_by(name=genre).one_or_none()
          if fetch_genre:
            # if found a genre, append it to the list
            venue.genres.append(fetch_genre)
          else:
            # fetch_genre returned None, so it is created
            new_genre = Genre(name=genre)
            db.session.add(new_genre)
            venue.genres.append(new_genre)


        db.session.add(venue)
        db.session.commit()
        # on successful db insert, flash success
        flash('Venue ' + request.form['name']  + ' was successfully listed!')
      except:
        print(sys.exc_info())
        db.session.rollback()
        flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.  see: http://flask.pocoo.org/docs/1.0/patterns/flashing/')
      finally:
        db.session.close()
        # TODO: on unsuccessful db insert, flash an error instead.
        # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
        # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
      return redirect(url_for('index'))

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  venue = Venue.query.get(venue_id)
  try: 
    db.session.delete(venue)
    db.session.commit()
  except:
    db.session.rollback()
  finally:
    db.session.close()

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return redirect(url_for('index'))

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  artists = Artist.query.all()
  data = []
  for artist in artists:
    data.append({
      "id": artist.id,
      "name": artist.name
    })
  # data=[{
  #   "id": 4,
  #   "name": "Guns N Petals",
  # }, {
  #   "id": 5,
  #   "name": "Matt Quevedo",
  # }, {
  #   "id": 6,
  #   "name": "The Wild Sax Band",
  # }]
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_term = request.form.get('search_term', '').strip()

  artists = Artist.query.filter(Artist.name.ilike('%' + search_term + '%')).all()
  artist_list = []

  for artist in artists:
    artist_shows = Show.query.filter_by(artist_id=artist.id).all()
    num_upcoming = 0

    for show in artist_shows:
      if show.show_time > datetime.now():
        num_upcoming += 1

    artist_list.append({
      "id": artist.id,
      "name": artist.name,
      "num_upcoming_shows": num_upcoming 
    })

  response = {
    "count": len(artists),
    "data": artist_list
  }
            
  # response={
  #   "count": 1,
  #   "data": [{
  #     "id": 4,
  #     "name": "Guns N Petals",
  #     "num_upcoming_shows": 0,
  #   }]
  # }
  return render_template('pages/search_artists.html', results=response, search_term=search_term)

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  artist = Artist.query.get(artist_id)

  genres = []
  for genre in artist.genres:
    genres.append(genre.name)

  # upcoming_shows = []
  # upcoming_shows_count = 0
  # past_shows = []
  # past_shows_count = 0

  # for show in artist.shows:
  #   if show.start_time > datetime.now():
  #     upcoming_shows_count += 1
  #     upcoming_shows.append({
  #       "venue_id": show.venue_id,
  #       "venue_name": show.venue.name,
  #       "venue_image_link": show.venue.image_link,
  #       "start_time": format_datetime(str(show.start_time))
  #       })
  #   else:
  #     past_shows_count += 1
  #     past_shows.append({
  #       "venue_id": show.venue_id,
  #       "venue_name": show.venue.name,
  #       "venue_image_link": show.venue.image_link,
  #       "start_time": format_datetime(str(show.start_time))
  #     })

  past_shows_query = db.session.query(Show).join(Venue).filter(Show.artist_id==artist_id).filter(Show.start_time<datetime.now()).all()   
  past_shows = []
  past_shows_count = db.session.query(Show).join(Venue).filter(Show.artist_id==artist_id).filter(Show.start_time<datetime.now()).count()
  for show in past_shows_query:
      past_shows.append({
        "venue_id": show.venue_id,
        "venue_name": show.venue.name,
        "venue_image_link": show.venue.image_link,
        "start_time": format_datetime(str(show.start_time))
      })

  upcoming_shows_query = db.session.query(Show).join(Venue).filter(Show.artist_id==artist_id).filter(Show. start_time>datetime.now()).all()   
  upcoming_shows = []
  upcoming_shows_count = db.session.query(Show).join(Venue).filter(Show.artist_id==artist_id).filter(Show. start_time>datetime.now()).count() 
  for show in upcoming_shows_query:
    upcoming_shows.append({
      "venue_id": show.venue_id,
      "venue_name": show.venue.name,
      "venue_image_link": show.venue.image_link,
      "start_time": format_datetime(str(show.start_time))
    })
  
  
  data = {
    "id": artist.id,
    "name": artist.name,
    "genres": genres,
    "city": artist.city,
    "state": artist.state,
    "phone": (artist.phone[:3] + '-' + artist.phone[3:6] + '-' + artist.phone[6:]),
    "website": artist.website,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": past_shows_count,
    "upcoming_shows_count": upcoming_shows_count,
  }

  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  # data1={
    # "id": 4,
    # "name": "Guns N Petals",
    # "genres": ["Rock n Roll"],
    # "city": "San Francisco",
    # "state": "CA",
    # "phone": "326-123-5000",
    # "website": "https://www.gunsnpetalsband.com",
    # "facebook_link": "https://www.facebook.com/GunsNPetals",
    # "seeking_venue": True,
    # "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
    # "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    # "past_shows": [{
    #   "venue_id": 1,
    #   "venue_name": "The Musical Hop",
    #   "venue_image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
    #   "start_time": "2019-05-21T21:30:00.000Z"
    # }],
    # "upcoming_shows": [],
    # "past_shows_count": 1,
    # "upcoming_shows_count": 0,
  # }
  # data2={
  #   "id": 5,
  #   "name": "Matt Quevedo",
  #   "genres": ["Jazz"],
  #   "city": "New York",
  #   "state": "NY",
  #   "phone": "300-400-5000",
  #   "facebook_link": "https://www.facebook.com/mattquevedo923251523",
  #   "seeking_venue": False,
  #   "image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
  #   "past_shows": [{
  #     "venue_id": 3,
  #     "venue_name": "Park Square Live Music & Coffee",
  #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #     "start_time": "2019-06-15T23:00:00.000Z"
  #   }],
  #   "upcoming_shows": [],
  #   "past_shows_count": 1,
  #   "upcoming_shows_count": 0,
  # }
  # data3={
  #   "id": 6,
  #   "name": "The Wild Sax Band",
  #   "genres": ["Jazz", "Classical"],
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "432-325-5432",
  #   "seeking_venue": False,
  #   "image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "past_shows": [],
  #   "upcoming_shows": [{
  #     "venue_id": 3,
  #     "venue_name": "Park Square Live Music & Coffee",
  #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #     "start_time": "2035-04-01T20:00:00.000Z"
  #   }, {
  #     "venue_id": 3,
  #     "venue_name": "Park Square Live Music & Coffee",
  #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #     "start_time": "2035-04-08T20:00:00.000Z"
  #   }, {
  #     "venue_id": 3,
  #     "venue_name": "Park Square Live Music & Coffee",
  #     "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
  #     "start_time": "2035-04-15T20:00:00.000Z"
  #   }],
  #   "past_shows_count": 0,
  #   "upcoming_shows_count": 3,
  # }
  # data = list(filter(lambda d: d['id'] == artist_id, [data1, data2, data3]))[0]
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.get(artist_id)
  
  #prepopulate form
  form.name.data = artist.name
  form.city.data = artist.city
  form.state.data = artist.state
  form.phone.data = artist.phone
  form.website_link.data = artist.website
  form.facebook_link.data = artist.facebook_link
  form.seeking_venue.data = artist.seeking_venue
  form.seeking_description.data = artist.seeking_description
  form.image_link.data = artist.image_link

  genres = []
  for genre in artist.genres:
    genres.append(genre.name)

  form.genres.data = genres

  artist={
    "id": artist.id,
    "name": artist.name,
    "genres": genres,
    "city": artist.city,
    "state": artist.state,
    "phone": (artist.phone[:3] + '-' + artist.phone[3:6] + '-' + artist.phone[6:]),
    "website": artist.website,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link
  }

  # artist = {
    #     "id": 4,
    #     "name": "Guns N Petals",
    #     "genres": ["Rock n Roll"],
    #     "city": "San Francisco",
    #     "state": "CA",
    #     "phone": "326-123-5000",
    #     "website": "https://www.gunsnpetalsband.com",
    #     "facebook_link": "https://www.facebook.com/GunsNPetals",
    #     "seeking_venue": True,
    #     "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
    #     "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
    # }

  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  form = ArtistForm(request.form)

  name = form.name.data
  city = form.city.data
  state = form.state.data
  phone = form.phone.data
  genres = form.genres.data
  seeking_description = form.seeking_description.data
  image_link = form.image_link.data
  website = form.website_link.data
  facebook_link = form.facebook_link.data
  if form.seeking_venue.data == "Yes":
    seeking_venue = True
  else:
    seeking_venue = False

  try:
    artist = Artist.query.get(artist_id)

    artist.name = name
    artist.city = city
    artist.state = state
    artist.phone = phone
    artist.seeking_venue = seeking_venue
    artist.seeking_description = seeking_description
    artist.image_link = image_link
    artist.website = website
    artist.facebook_link = facebook_link
    
    # similar to the edit venue controller
    artist.genres = []
    for genre in genres:
      query_genre = Genre.query.filter_by(name=genre).one_or_none() 
      if query_genre:
        artist.genres.append(query_genre)
      else:
        new_genre = Genre(name=genre)
        db.session.add(new_genre)
        artist.genres.append(new_genre)

    db.session.commit()
    flash('Edit ' + name + ' was successfully edited!')
  except:
    db.session.rollback()
    flash('Edit ' + name + ' failed!')
  finally:
    db.session.close()


  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()

  venue = Venue.query.get(venue_id)
  
  #prepopulate form
  form.name.data = venue.name
  form.city.data = venue.city
  form.state.data = venue.state
  form.address.data = venue.address
  form.phone.data = venue.phone
  form.website_link.data = venue.website
  form.facebook_link.data = venue.facebook_link
  form.seeking_talent.data = venue.seeking_talent
  form.seeking_description.data = venue.seeking_description
  form.image_link.data = venue.image_link

  genres = []
  for genre in venue.genres:
    genres.append(genre.name)

  form.genres.data = genres

  venue={
    "id": venue.id,
    "name": venue.name,
    "genres": genres,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": (venue.phone[:3] + '-' + venue.phone[3:6] + '-' + venue.phone[6:]),
    "website": venue.website,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link
  }


  # venue={
  #   "id": 1,
  #   "name": "The Musical Hop",
  #   "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
  #   "address": "1015 Folsom Street",
  #   "city": "San Francisco",
  #   "state": "CA",
  #   "phone": "123-123-1234",
  #   "website": "https://www.themusicalhop.com",
  #   "facebook_link": "https://www.facebook.com/TheMusicalHop",
  #   "seeking_talent": True,
  #   "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
  #   "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
  # }
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes

  form = VenueForm(request.form) # got a type error when i didn't add request.form to VenueForm()

  name = form.name.data
  city = form.city.data
  state = form.state.data
  address = form.state.data
  phone = form.phone.data
  genres = form.genres.data
  seeking_description = form.seeking_description.data
  image_link = form.image_link.data
  website = form.website_link.data
  facebook_link = form.facebook_link.data
  if form.seeking_talent.data == "Yes":
    seeking_talent = True
  else:
    seeking_talent = False

  try:
    venue = Venue.query.get(venue_id)

    venue.name = name
    venue.city = city
    venue.state = state
    venue.address = address
    venue.phone = phone
    venue.seeking_talent = seeking_talent
    venue.seeking_description = seeking_description
    venue.image_link = image_link
    venue.website = website
    venue.facebook_link = facebook_link
    
    # create or persist genres, add tp venue.genres list
    venue.genres = []
    for genre in genres:
      query_genre = Genre.query.filter_by(name=genre).one_or_none() 
      if query_genre:
        venue.genres.append(query_genre)
      else:
        new_genre = Genre(name=genre)
        db.session.add(new_genre)
        venue.genres.append(new_genre)

    db.session.commit()
    flash('Edit ' + name + ' was successfully edited!')
  except:
    db.session.rollback()
    flash('Edit ' + name + ' failed!')
  finally:
    db.session.close()


  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  
  form = ArtistForm(request.form)
  if form.seeking_venue.data == 'Yes':
    seeking_venue = True
  else:
    seeking_venue = False

  phone = form.phone.data
  validate_phone = re.compile(r'[0-9()+/s]+')

  while not validate_phone.match(phone):
    flash('phone number is not valid')
    return redirect(url_for('create_artist_submission'))

  if not form.validate():
        flash( form.errors )
        return redirect(url_for('create_artist_submission'))  
  else:
      error_in_insert = False
      phone = re.sub('\D', '',  phone)
  
      try:
        artist = Artist(name=form.name.data, city=form.city.data, state=form.state.data, phone=phone, 
                        image_link=form.image_link.data, facebook_link=form.facebook_link.data, website=form.website_link.data, 
                        seeking_description=form.seeking_description.data, seeking_venue=seeking_venue)

        genres = form.genres.data
        for genre in genres:
          fetch_genre = Genre.query.filter_by(name=genre).one_or_none()
          if fetch_genre:
            # if found a genre, append it to the list
            artist.genres.append(fetch_genre)
          else:
            # fetch_genre was None. It's not created yet, so create it
            new_genre = Genre(name=genre)
            db.session.add(new_genre)
            artist.genres.append(new_genre)

        db.session.add(artist)
        db.session.commit()
        # on successful db insert, flash success
        flash('Venue ' + request.form['name']  + ' was successfully listed!')
      except:
        db.session.rollback()
        flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
      finally:
        db.session.close()

      # TODO: on unsuccessful db insert, flash an error instead.
      # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
      return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.

  shows = Show.query.all()
  data = []

  for show in shows: 
    data.append({
      "venue_id": show.venue.id,
      "venue_name": show.venue.name,
      "artist_id": show.artist.id,
      "artist_name": show.artist.name,
      "artist_image_link": show.artist.image_link,
      "start_time": format_datetime(str(show.start_time))
    })


  # data=[{
  #   "venue_id": 1,
  #   "venue_name": "The Musical Hop",
  #   "artist_id": 4,
  #   "artist_name": "Guns N Petals",
  #   "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
  #   "start_time": "2019-05-21T21:30:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 5,
  #   "artist_name": "Matt Quevedo",
  #   "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
  #   "start_time": "2019-06-15T23:00:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 6,
  #   "artist_name": "The Wild Sax Band",
  #   "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "start_time": "2035-04-01T20:00:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 6,
  #   "artist_name": "The Wild Sax Band",
  #   "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "start_time": "2035-04-08T20:00:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 6,
  #   "artist_name": "The Wild Sax Band",
  #   "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "start_time": "2035-04-15T20:00:00.000Z"
  # }]
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  form = ShowForm(request.form)

  show = Show(artist_id=form.artist_id.data, venue_id=form.venue_id.data, start_time=form.start_time.data)

  try: 
    db.session.add(show)
    db.session.commit()
    flash('Show was successfully listed!')
  except:
    db.session.rollback()
    flash('An error occurred. Show could not be listed. see: http://flask.pocoo.org/docs/1.0/patterns/flashing/')
  finally: 
    db.session.close

  # on successful db insert, flash success
  # flash('Show was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
