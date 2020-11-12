#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
import sys
import random
from flask import Flask, render_template, request, Response, flash, redirect, url_for, jsonify, abort
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
from datetime import date, datetime
from sqlalchemy import join
from sqlalchemy.orm import sessionmaker


#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# app = Flask(__name__)

# app.config.from_object('config')
# app.config['SQLALCHEMY_DATABASE_URI'] ='postgresql://Tyler:Pesthlos!2772@localhost:5432/fyyur'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# app.debug = True

db = SQLAlchemy(app)

# TODO: connect to a local postgresql database

migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#
venue_genres = db.Table('venue_genres',
    db.Column('venue_id', db.Integer, db.ForeignKey('venues.id'), primary_key=True),
    db.Column('genre_id', db.Integer, db.ForeignKey('genres.id'), primary_key=True)
)


class Venue(db.Model):
    __tablename__ = 'venues'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    website = db.Column(db.String(120))
    facebook_link = db.Column(db.String(120))
    shows = db.relationship('Show', backref='venue_shows')
    genres = db.relationship('Genre', secondary=venue_genres,
      backref=db.backref('venues', lazy=True))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

    def __repr__(self):
        return f'<Venue{self.id} {self.name} {self.city}>'

artist_genres = db.Table('artist_genres',
    db.Column('artist_id', db.Integer, db.ForeignKey('artists.id'), primary_key=True),
    db.Column('genre_id', db.Integer, db.ForeignKey('genres.id'), primary_key=True)
)

class Artist(db.Model):
    __tablename__ = 'artists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    website = db.Column(db.String(120))
    facebook_link = db.Column(db.String(120))
    shows = db.relationship('Show', backref='artist_shows')
    genres = db.relationship('Genre', secondary=artist_genres,
      backref=db.backref('artists', lazy=True))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

    def __repr__(self):
        return f'<Artist{self.id} {self.name}>'

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class Show(db.Model):
    __tablename__ = 'shows'

    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime)
    venue_id = db.Column(db.Integer,  db.ForeignKey(
        'venues.id'), nullable=False)
    artist_id = db.Column(db.Integer,  db.ForeignKey(
        'artists.id'), nullable=False)

    
    def __repr__(self):
        return f'<Show{self.id} {self.start_time} venId:{self.venue_id} artistId:{self.artist_id}>'


class Genre(db.Model):
    __tablename__ = 'genres'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String())
    
    def __repr__(self):
        return f'<Genre{self.id} {self.name}>'


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Helpers.
#----------------------------------------------------------------------------#

def get_genres(genre_list):
  genres = []
  for genre in genre_list:
    genres.append(genre.name)
  return genres

def query_genres(genre_list):
    genres = []
    for genre in genre_list:
      new_genre = Genre.query.filter(Genre.name == genre).one()
      genres.append(new_genre)
    return genres

def generate_random_pic():
    random_choice = random.randrange(3)
    generic_pic_urls = ['https://scontent-bos3-1.xx.fbcdn.net/v/t31.0-8/1973307_1407244406211531_1108234767_o.jpg?_nc_cat=105&ccb=2&_nc_sid=e3f864&_nc_ohc=h0K2-4-1IcEAX-u52BX&_nc_ht=scontent-bos3-1.xx&oh=86cd77ec3480081eaf006584af659c52&oe=5FD06D97', 'https://cdn.pixabay.com/photo/2014/04/05/11/09/concert-314851_1280.jpg', 'https://pbs.twimg.com/profile_images/875130202787004417/O-zMkA97_400x400.jpg']
    return generic_pic_urls[random_choice]
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
  #       num_shows should be aggregated based on number of upcoming shows per venue.

  def to_array(rows):
    return [r._asdict() for r in rows]

  def query(query):
    data = query
    return to_array(data)

  cities = query(Venue.query.with_entities(Venue.city).distinct().all())
  data = []

  for city in cities:
    city = city['city']
    state = Venue.query.filter(Venue.city == city).with_entities(Venue.state).distinct().one()._asdict()['state']
    city_venues = {
      'city': city,
      'state': state,
      'venues': []
    }
    venues_in_city = Venue.query.filter(Venue.city == city)
    for venue in venues_in_city:
      city_venue = {
        'id': venue.id,
        'name': venue.name,
      }
      shows = db.session.query(Show).join(Venue).filter(Show.venue_id == venue.id).all()
      num_upcoming_shows = 0
      if len(shows) > 0:
        for show in shows:
          if datetime.now() < show.start_time:
            num_upcoming_shows += 1
      city_venue['num_upcoming_shows'] = num_upcoming_shows
      city_venues['venues'].append(city_venue)
    data.append(city_venues)
  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"

  search_term=request.form.get('search_term', '')

  search_venues = Venue.query.filter(Venue.name.ilike(f'%{search_term}%') ).all()
  search_cities = Venue.query.filter(Venue.city.ilike(f'{search_term}') ).all()


  for venue in search_cities:
    if venue not in search_venues:
      search_venues.append(venue)
  

  response={
    "count": 0,
    "data": []
  }

  for venue in search_venues:
    response['count'] += 1
    upcoming_shows = Show.query.join(Venue).filter(Show.start_time > datetime.now()).all()
    ven_obj = {
      "id": venue.id,
      "name": venue.name,
      "num_upcoming_shows": len(upcoming_shows),
    }
    response['data'].append(ven_obj)
    
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id

  venue =  Venue.query.filter(Venue.id == venue_id).first()
  artist_shows = db.session.query(Show, Artist).join(Artist).filter(Show.venue_id == venue_id).all()

  data = {
    "id": venue.id,
    "name": venue.name,
    "genres": get_genres(venue.genres),
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website,
    "facebook_link": venue.facebook_link,
    "seeking_talent": True,
    "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    "image_link": venue.image_link or generate_random_pic(),
    "past_shows": [],
    "upcoming_shows": [],
    "past_shows_count": 0,
    "upcoming_shows_count": 0
  }
  if len(artist_shows) > 0:
    upcoming_shows = []
    past_shows = []
    for show in artist_shows:
      s = show.Show
      artist = show.Artist
      start_time = s.start_time
      show_artist_info = {
        "artist_id": artist.id,
        "artist_name": artist.name,
        "artist_image_link": artist.image_link or generate_random_pic(),
        "start_time": start_time.strftime('%m-%d-%y, %H:%M:%S')
      }
      if start_time > datetime.now():
        data['upcoming_shows'].append(show_artist_info)
        data['upcoming_shows_count'] += 1
      else:
        data['past_shows'].append(show_artist_info)
        data['past_shows_count'] += 1
      
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
  error = False
  body = {}
  try:
    data = request.form    
    genres = data.getlist('genres')
    
    venue = Venue(name=data['name'], city=data['city'], state=data['state'], address=data['address'], phone=data['phone'], website=data['website'], facebook_link=data['facebook_link'])

    for genre in genres:
      new_genre = db.session.query(Genre).filter(Genre.name == genre).one()
      venue.genres.append(new_genre)
    
    db.session.add(venue)
    db.session.commit()
  except:
      db.session.rollback()
      error = True
      print(sys.exc_info())
  finally:
      db.session.close()
  if error:
      # TODO: on unsuccessful db insert, flash an error instead.
      flash('An error occurred. Venue ' + data['name'] + ' could not be listed.')
  else:
      # on successful db insert, flash success
      flash('Venue ' + request.form['name'] + ' was successfully listed!')

  # TODO: modify data to be the data object returned from db insertion
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  error = False
  body = {}
  try:
    venue = Venue.query.filter(Venue.id == venue_id).first()
    venue_name = venue.name
    for show in venue.shows:
      db.session.delete(show)

    db.session.delete(venue)
    db.session.commit()
  except:
    db.session.rollback()
    error = True
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    # TODO: on unsuccessful db insert, flash an error instead.
    flash('An error occurred. Venue ' + venue_name + ' could not be deleted.')
  else:
    # on successful db insert, flash success
    flash('Venue ' + venue_name + ' was successfully deleted!')

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return redirect(url_for('index'))

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  artists = Artist.query.all()
  return render_template('pages/artists.html', artists=artists)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".

  search_term=request.form.get('search_term', '')

  search_artists = Artist.query.filter(Artist.name.ilike(f'%{search_term}%')).all()

  response={
    "count": 0,
    "data": []
  }

  for artist in search_artists:
    response['count'] += 1
    upcoming_shows = Show.query.join(Artist).filter(Show.start_time > datetime.now()).all()
    art_obj = {
      "id": artist.id,
      "name": artist.name,
      "num_upcoming_shows": len(upcoming_shows),
    }
    response['data'].append(art_obj)
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  artist =  Artist.query.filter(Artist.id == artist_id).first()
  venue_shows = db.session.query(Show, Venue).join(Venue).filter(Show.artist_id == artist_id).all()

  data = {
    "id": artist.id,
    "name": artist.name,
    "genres": get_genres(artist.genres),
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website,
    "facebook_link": artist.facebook_link,
    "seeking_venue": True,
    "seeking_description": f'Looking for shows to perform at in the {artist.city}, {artist.state} Area!',
    "image_link": artist.image_link or generate_random_pic(),
    "past_shows": [],
    "upcoming_shows": [],
    "past_shows_count": 0,
    "upcoming_shows_count": 0
  }
  if len(venue_shows) > 0:
    upcoming_shows = []
    past_shows = []
    for show in venue_shows:
      s = show.Show
      venue = show.Venue
      start_time = s.start_time
      show_venue_info = {
          "venue_id": venue.id,
          "venue_name": venue.name,
          "venue_image_link": venue.image_link,
          "start_time": start_time.strftime('%m-%d-%y, %H:%M:%S')
      }
      if start_time > datetime.now():
        data['upcoming_shows'].append(show_venue_info)
        data['upcoming_shows_count'] += 1
      else:
        data['past_shows'].append(show_venue_info)
        data['past_shows_count'] += 1
  
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.filter(Artist.id == artist_id).first()

  artist = {
    "id": artist.id,
    "name": artist.name,
    "genres": get_genres(artist.genres),
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website,
    "facebook_link": artist.facebook_link,
    "seeking_venue": True,
    "seeking_description": f'Looking for shows to perform at in the {artist.city}, {artist.state} Area!',
    "image_link": artist.image_link
  }
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  error = False
  body = {}
  try:
    data = request.form

    genres = query_genres(data.getlist('genres'))
    artist = Artist.query.filter(Artist.id == artist_id).first()

    artist.name = data['name']
    artist.city = data['city']
    artist.state = data['state']
    artist.phone = data['phone']
    artist.website = data['website']
    artist.facebook_link = data['facebook_link']
    artist.image_link = data['image_link']
    artist.genres = genres

    db.session.add(artist)
    db.session.commit()
  except:
    db.session.rollback()
    error = True
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    # TODO: on unsuccessful db insert, flash an error instead.
    flash('An error occurred. Artist ' + data['name'] + ' could not be edited.')
  else:
    # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully edited!')


  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()

  venue = Venue.query.filter(Venue.id == venue_id).first()

  venue = {
    "id": venue.id,
    "name": venue.name,
    "genres": get_genres(venue.genres),
    "address": "1015 Folsom Street",
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website,
    "facebook_link": venue.facebook_link,
    "seeking_venue": True,
    "seeking_description": "We are on the lookout for a local venue to play every two weeks. Please call us.",
    "image_link": venue.image_link
  }
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes

  error = False
  body = {}
  try:
    data = request.form

    genres = query_genres(data.getlist('genres'))
    venue = Venue.query.filter(Venue.id == venue_id).first()

    venue.name = data['name']
    venue.address = data['address']
    venue.city = data['city']
    venue.state = data['state']
    venue.phone = data['phone']
    venue.website = data['website']
    venue.facebook_link = data['facebook_link']
    venue.image_link = data['image_link']
    venue.genres = genres

    db.session.add(venue)
    db.session.commit()
  except:
    db.session.rollback()
    error = True
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    # TODO: on unsuccessful db insert, flash an error instead.
    flash('An error occurred. Venue ' + data['name'] + ' could not be edited.')
  else:
    # on successful db insert, flash success
    flash('Venue ' + request.form['name'] + ' was successfully edited!')
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
  error = False
  body = {}
  try:
    data = request.form    
    genres = data.getlist('genres')
    
    artist = Artist(name=data['name'], city=data['city'], state=data['state'], phone=data['phone'], website=data['website'], facebook_link=data['facebook_link'])
    
    for genre in genres:
      new_genre = db.session.query(Genre).filter(Genre.name == genre).one()
      artist.genres.append(new_genre)
    
    db.session.add(artist)
    db.session.commit()
  except:
      db.session.rollback()
      error = True
      print(sys.exc_info())
  finally:
      db.session.close()
  if error:
      # TODO: on unsuccessful db insert, flash an error instead.
      flash('An error occurred. Artist ' + data['name'] + ' could not be listed.')
  else:
      # on successful db insert, flash success
      flash('Artist ' + request.form['name'] + ' was successfully listed!')

  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  
  def to_array(rows):
    return [r._asdict() for r in rows]

  def query(query):
    data = query
    return to_array(data)

  venue_artist_shows = db.session.query(Show, Venue, Artist).join(Venue).join(Artist).order_by(Show.start_time.desc()).all()

  data = []
  for show in venue_artist_shows:
    show_time = show.Show.start_time.strftime('%m-%d-%y, %H:%M:%S')
    s = {
      "venue_id": show.Venue.id,
      "venue_name": show.Venue.name,
      "artist_id": show.Artist.id,
      "artist_name": show.Artist.name,
      "artist_image_link": show.Artist.image_link or generate_random_pic(),
      "start_time": show_time
    }
    data.append(s)

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
  error = False
  body = {}
  try:
    data = request.form    
    
    show = Show(start_time=data['start_time'], venue_id=data['venue_id'], artist_id=data['artist_id'])

    artist = Artist.query.filter(Artist.id == show.artist_id).one().name
    venue = Venue.query.filter(Venue.id == show.venue_id).one().name

    db.session.add(show)
    db.session.commit()
  except:
      db.session.rollback()
      error = True
      print(sys.exc_info())
  finally:
      db.session.close()
  if error:
      # TODO: on unsuccessful db insert, flash an error instead.
      flash(f'An error occurred. {artist}\'s show at {venue} could not be listed.')
  else:
      # on successful db insert, flash success
      flash(f'{artist}\'s show at {venue} successfully listed!')

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
