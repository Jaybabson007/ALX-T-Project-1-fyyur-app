#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
import collections
from collections.abc import Callable
from distutils.log import error
from importlib.metadata import metadata
import json
from tkinter import CASCADE
from tkinter.messagebox import YES
import dateutil.parser
import datetime
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, ForeignKey, Integer, String,schema
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from flask_wtf.csrf import CSRFProtect
from forms import VenueForm, ArtistForm, ShowForm
from forms import *
from flask_migrate import Migrate
import sys, traceback


#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
CSRFProtect(app)
db = SQLAlchemy(app)
Base = declarative_base

migrate = Migrate(app, db)

# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

#show = db.Table('Show',
 # db.Column("Show_id",db.Integer, primary_key=True),
  #db.Column("Artist_id",db.Integer, db.ForeignKey('Artist.id'), nullable=False),
  #db.Column("Venue_id",db.Integer, db.ForeignKey('Venue.id'), nullable=False),
  #db.Column("Start_time",db.DateTime())
#)


class Show(db.Model):
    __tablename__ = 'Show'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
    start_time = db.Column(db.DateTime())

def __repr__(self):
  return f'<Show ID: {self.id} Artist ID: {self.artist_id} Venue ID: {self.venue_id}>'


class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=YES)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String))
    facebook_link = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    website_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(500))

    artists = db.relationship('Artist',secondary='shows', backref=db.backref('venues', lazy=True))

    def __repr__(self):
      return f'<Venue {self.id} {self.name}>'
        

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String,nullable=YES)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String))
    facebook_link = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    website_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(500))

    def __repr__(self):
      return f'<Artist {self.id} {self.name}>'

    # TODO: implement any missing fields, as a database migration using Flask-Migrate



def show_as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

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
  
  
  """ 
  Code for listing venue by city and state 
  inspired from this Github repo: https://github.com/alexsandberg

  """
  
  data=[]

  venues = Venue.query.all()
  venue_cities = set()
  for venue in venues:
    venue_cities.add((venue.city, venue.state))


  for location in venue_cities:
    data.append({
      'city': location[0],
      'state': location[1],
      'venues': []
    })


    for venue in venues:
      num_upcoming_shows = 0

      shows = Show.query.filter_by(venue_id=venue.id)

      for show in shows:
        if show.start_time > datetime.now():
          num_upcoming_shows += 1

      for entry in data:
        if venue.city == entry['city'] and venue.state == entry['state']:
          entry['venues'].append({
            "id": venue.id,
            "name": venue.name,
            "num_upcoming_shows": num_upcoming_shows
          })
    return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search = request.form.get('search_term')
  response=Venue.query.filter(Venue.name.ilike('%{}%'.format(search))).all()
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id

  venue = Venue.query.filter_by(id=venue_id).first()

  shows = Show.query.filter_by(id=venue_id).all()

  def upcoming_shows():
    upcoming = []

    for show in shows:
      if show.start_time > datetime.now():
        upcoming.append({
          'artist_id':show.artist_id,
          'artist_name':Artist.query.filter_by(id=show.artist_id).first().name,
          'artist_image_link':Artist.query.filter_by(id=show.artist_id).first().image_link,
          'start_time':format_datetime(str(show.start_time))
        })
      return upcoming

  def past_shows():
    past = []

    for show in shows:
      if show.start_time < datetime.now():
        past.append({
          'artist_id': show.artist_id,
          'artist_name': Artist.query.filter_by(id=show.artist_id).first().name,
          'artist_image_link': Artist.query.filter_by(id=show.artist_id).first().image_link,
          'start_time': format_datetime(str(show.start_time))
        })
      return past
        

  data={
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "facebook_link": venue.facebook_link,
    "image_link": venue.image_link,
    "website": venue.website,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "past_shows": past_shows(),
    "upcoming_shows": upcoming_shows(),
    "past_shows_count": len(past_shows()),
    "upcoming_shows_count": len(upcoming_shows())
  }
 
 
  data = list(filter(lambda d: d['id'] == venue_id, [data]))[0]
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------



""" 
  Code for creating venue
  inspired from this Github repo: https://github.com/brunogarcia

  """
@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  
  error = False
  form = VenueForm()

 

  if True: #perfect validation
   #return redirect(url_for('create_venue_form'))
    
    try:
        venue = Venue(
          name = form.name.data,
          city = form.city.data,
          state = form.state.data,
          address = form.address.data,
          phone = form.phone.data,
          genres = ','.join(form.genres.data),
          facebook_link = form.facebook_link.data,
          image_link = form.image_link.data,
          website_link = form.website_link.data,
          seeking_talent = form.seeking_talent.data,
          seeking_description = form.seeking_description.data
        )
        print(venue)
        exit()
        db.session.add(venue)
        db.session.commit()

    except:
      error = True
      db.session.rollback()
      print(sys.exc_info())

    finally:
      db.session.close()
  else:
    print("Error validating")
    
  
  # on successful db insert, flash success
  if not error:
    flash('Venue ' + request.form['name'] + ' was successfully listed!')

  # TODO: on unsuccessful db insert, flash an error instead.
  if error:
    flash('Venue ' + request.form['name'] + ' could not be listed.')

  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  error = False 

  try:
    venue = Venue.query.get(venue_id)
    db.sesion.delete()
    db.session.commit()
    flash('Venue deleted successfully!')
    
  except:
    db.session.rollback()
    flash('Oops! Venue cannot be deleted!')

  finally:
    db.session.close()


  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return render_template('pages/home.html')

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  data=[]

  artists = Artist.query.all()

  for artist in artists:
    data.append({
      "id": artist.id,
      "name": artist.name
    })
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".

    search = request.form.get('search_term')
    response= Artist.query.filter(Artist.name.ilike('%{}%'.format(search))).all()

    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  
    artist = Artist.query.filter_by(id=artist_id).first()

    shows = Show.Query.filter_by(artist_id).all


    def upcoming_shows():
      upcoming = []


      for show in shows:
        if show.start_time > datetime.now():
          upcoming.append({
            "venue_id": show.venue_id,
            "venue_name": Venue.query.filter_by(id=show.venue_id).first().name,
            "venue_image_link": Venue.query.filter_by(id=show.venue_id).first().image_link,
            "start_time": format_datetime(str(show.start_time))
          })
      return upcoming


    def past_shows():
      past = []


      for show in shows:
        if show.start_time < datetime.now():
          past.append({
            "venue_id": show.venue_id,
            "venue_name": Venue.query.filter_by(id=show.venue_id).first().name,
            "venue_image_link": Venue.query.filter_by(id=show.venue_id).first().image_link,
            "start_time": format_datetime(str(show.start_time))
          })
      return past
    
    data={
      "id": artist.id,
      "name": artist.name,
      "city": artist.city,
      "state": artist.state,
      "phone": artist.phone,
      "genres": artist.genres,
      "facebook_link": artist.facebook_link,
      "image_link": artist.image_link,
      "website": artist.website,
      "seeking_venue": artist.seeking_venue,
      "seeking_description": artist.seeking_description,
      "past_shows": past_shows(),
      "upcoming_shows": upcoming_shows(),
      "past_shows_count": len(past_shows()),
      "upcoming_shows_count": len(upcoming_shows()),
    }

    data = list(filter(lambda d: d['id'] == artist_id, [data]))[0]
    return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  
  artist= ArtistForm.query.filter(Artist.id == artist_id).first()

  

  form.name.data = artist.name
  form.city.data = artist.city
  form.state.data = artist.state
  form.phone.data = artist.phone
  form.genres.data = artist.genres
  form.facebook_link.data = artist.facebook_link
  form.image_link.data = artist.image_link
  form.website_link.data = artist.website_link
  form.seeking_venue.data = artist.seeking_venue
  form.seeking_description.data = artist.seeking_description

  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  error = False

  name = request.form['name']
  city = request.form['city']
  state = request.form['state']
  phone = request.form['phone']
  genres = request.form.getlist('genres')
  facebook_link = request.form['facebook_link']
  image_link = request.form['image_link']
  website = request.form['website']
  seeking_talent = True if 'seeking_talent' in request.form else False
  seeking_description = request.form['seeking_description']

  try:
    artist = Artist.query.get(artist_id)

    artist.name = name
    artist.city = city
    artist.state = state
    artist.phone = phone
    artist.genres = genres
    artist.image_link = image_link
    artist.facebook_link = facebook_link
    artist.website = website
    artist.seeking_talent = seeking_talent
    artist.seeking_description = seeking_description

    db.session.commit()

  except Exception:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  
  finally:
    db.session.close()

  if not error: 
    flash('Artist '+ name + ' was successfully updated!')

  if error:
     flash('An error occured. Artist '+ name + ' could not be updated.')


  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue= Venue.query.filter(Venue.id == venue_id)

  form.name.data = venue.name
  form.city.data = venue.city
  form.state.data = venue.state
  form.address.data = venue.address
  form.phone.data = venue.phone
  form.genres.data = venue.genres
  form.facebook_link.data = venue.facebook_link
  form.image_link.data = venue.image_link
  form.website_link.data = venue.website
  form.seeking_talent.data = venue.seeking_talent
  form.seeking_description.data = venue.seeking_description

  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  error = False

  name = request.form['name']
  city = request.form['city']
  state = request.form['state']
  address = request.form['address']
  phone = request.form['phone']
  genres = request.form.getlist('genres')
  image_link = request.form['image_link']
  facebook_link = request.form['facebook_link']
  website = request.form['website']
  seeking_talent = True if 'seeking_talent' in request.form else False
  seeking_description = request.form['seeking_description']

  try:
    venue = Venue.query.get(venue_id)

    venue.name = name
    venue.city = city
    venue.state = state
    venue.address = address
    venue.phone = phone
    venue.genres = genres
    venue.facebook_link = facebook_link
    venue.image_link = image_link
    venue.website = website
    venue.seeking_talent = seeking_talent
    
    db.session.commit()

  except Exception:
    error = True
    db.session.rollback()
    print(sys.exc_info())

  finally:
    db.session.close()

  if not error:
    flash('Venue '+ name + ' was successfully updated!')

  if error:
    flash('An error occured. Venue '+ name + ' could not be updated')


  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
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
  error = False
  form = ArtistForm(request.form)

  if form.validate():

    try:
      artist = Artist(
        name = form.name.data,
        city = form.city.data,
        state = form.state.data,
        phone = form.phone.data,
        genres = ','.join(form.genres.data),
        facebook_link = form.facebook_link.data,
        image_link = form.image_link.data,
        website_link = form.website_link.data,
        seeking_venue = form.seeking_venue.data,
        seeking_description = form.seeking_description.data
      )

      db.session.add(artist)
      db.session.commit()
    except:
      error = True
      db.session.rollback()
      print(sys.exc_info())
    finally:
      db.session.close()
  # on successful db insert, flash success
    if not error:
      flash('Artist ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
    if error:
      flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.

  shows = Show.query.all()

  data= []

  for show in shows:
    data.append({
        "venue_id": show.venue_id,
        "venue_name": Venue.query.filter_by(id=show.venue_id).first().name,
        "artist_id": show.artist_id,
        "artist_name": Artist.query.filter_by(id=show.artist_id).first().name,
        "artist_image_link": Artist.query.filter_by(id=show.artist_id).first().image_link,
        "start_time": format_datetime(str(show.start_time))
    })
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

  artist_id = request.form['artist_id']
  venue_id = request.form['venue_id']
  start_time = request.form['start_time']

  try:
    show = Show(
      artist_id=artist_id,
      venue_id=venue_id,
      start_time=start_time
    )

    db.session.add(show)
    db.session.commit()

  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())

  finally:
    db.session.close()


  # on successful db insert, flash success
  if not error:
    flash('Show was successfully listed!')

  # TODO: on unsuccessful db insert, flash an error instead.
  if error: 
    flash('An error occurred. Show could not be listed.')

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
