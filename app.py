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
from dateutil.parser import parse
import datetime
from datetime import date
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
csrf = CSRFProtect()


def create_app():
    app = Flask(__name__)
    csrf.init_app(app)

db = SQLAlchemy(app)
Base = declarative_base

migrate = Migrate(app, db)

# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#


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

    shows = db.relationship('Show', backref='Venue', lazy='joined', cascade='all, delete')

    def __repr__(self):
        return f'<Venue ID: {self.id}, Venue Name: {self.name}>'

    # Adding methods to get all of Venue data related to Artist and Show

    def venue_as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
        

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

    shows = db.relationship('Show', backref='Artist', lazy='joined', cascade='all, delete')

    def __repr__(self):
        return f'<Artist ID: {self.id}, Artist Name: {self.name}>'

  # Adding methods to get all of Artist data related to Venue and Show

    def artist_as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    # TODO: implement any missing fields, as a database migration using Flask-Migrate


class Show(db.Model):
    __tablename__ = 'Show'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
    start_time = db.Column(db.DateTime())

def __repr__(self):
  return f'<Show ID: {self.id} Artist ID: {self.artist_id} Venue ID: {self.venue_id}>'

# Adding methods to get all of Shows data related to Artist and venue

def show_as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

#Date format
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
  
  areas = list()
  all_venues = Venue.query.all()
  for venue in all_venues:
    area = dict()
    area_position = -1
    if len(areas) == 0:
      area_position = 0
      area = {
        'city': venue.city,
        'state': venue.state,
        'venues': list()
      }
      areas.append(area)
    else:
      for i, area in enumerate(areas):
        if area['city'] == venue.city and area['state'] == venue.state:
          area_position = i
          break
      if area_position < 0:
        area = {
        'city': venue.city,
        'state': venue.state,
        'venues': list()
      }
        areas.append(area)
        area_position = len(areas) - 1
      else:
        area = areas[area_position]
    num_upcoming_shows = Show.query.filter(
                    Show.start_time > datetime.now(),
                    Show.venue_id == venue.id).all()
    dic = { 'id': venue.id, 
            'name': venue.name, 
            'num_upcoming_shows': num_upcoming_shows
          }
    area['venues'].append(dic)
    areas[area_position] = area
  return render_template('pages/venues.html', areas=areas)


@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_term = request.form.get('search_term', '')

    # find all venues matching search term
    # including partial match and case-insensitive
  venues = Venue.query.filter(Venue.name.ilike(f'%{search_term}%')).all()

  response = {
        "count": len(venues),
        "data": []
    }

  for venue in venues:
        num_upcoming_shows = 0

        shows = Show.query.filter_by(venue_id=venue.id).all()

        # calculuate num of upcoming shows for each venue
        for show in shows:
            if show.start_time > datetime.now():
                num_upcoming_shows += 1
        # add venue data to response
        response['data'].append({
            "id": venue.id,
            "name": venue.name,
            "num_upcoming_shows": num_upcoming_shows,
        })

    # return response with search results
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))



@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id

  # get all venues
    venue = Venue.query.filter_by(id=venue_id).first()

    # get all shows for given venue
    shows = Show.query.filter_by(venue_id=venue_id).all()

    # returns upcoming shows
    def upcoming_shows():
        upcoming = []

        # if show is in future, add show details to upcoming
        for show in shows:
            if show.start_time > datetime.now():
                upcoming.append({
                    "artist_id": show.artist_id,
                    "artist_name": Artist.query.filter_by(id=show.artist_id).first().name,
                    "artist_image_link": Artist.query.filter_by(id=show.artist_id).first().image_link,
                    "start_time": format_datetime(str(show.start_time))
                })
        return upcoming

    # returns past shows
    def past_shows():
        past = []

        # if show is in past, add show details to past
        for show in shows:
            if show.start_time < datetime.now():
                past.append({
                    "artist_id": show.artist_id,
                    "artist_name": Artist.query.filter_by(id=show.artist_id).first().name,
                    "artist_image_link": Artist.query.filter_by(id=show.artist_id).first().image_link,
                    "start_time": format_datetime(str(show.start_time))
                })
        return past

    # data for given venue
    data = {
        "id": venue.id,
        "name": venue.name,
        "genres": venue.genres,
        "address": venue.address,
        "city": venue.city,
        "state": venue.state,
        "phone": venue.phone,
        "website_link": venue.website_link,
        "facebook_link": venue.facebook_link,
        "seeking_talent": venue.seeking_talent,
        "seeking_description": venue.seeking_description,
        "image_link": venue.image_link,
        "past_shows": past_shows(),
        "upcoming_shows": upcoming_shows(),
        "past_shows_count": len(past_shows()),
        "upcoming_shows_count": len(upcoming_shows())
    }

    # return template with venue data
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
  
  error = False
  form = VenueForm(request.form)

 
 # if form.validate():
  if True: #perfect validation    
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
        
        db.session.add(venue)
        db.session.commit()

    except:
      error = True
      db.session.rollback()
      print(sys.exc_info())

    finally:
      db.session.close()


  # on successful db insert, flash success
  if not error:
    flash('Venue ' + request.form['name'] + ' was successfully listed!')

  # TODO: on unsuccessful db insert, flash an error instead.
  if error:
    flash('Venue ' + request.form['name'] + ' could not be listed.')

  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')


  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  
@app.route('/venues/<int:venue_id>/delete')
def delete_venue(venue_id):
  
  try:
      venue = Venue.query.get(venue_id)
      db.session.delete(venue)
      db.session.commit()
      flash('Venue deleted successfully!')
  except:
      db.session.rollback()
      flash('Oops! Venue cannot be deleted!')
  finally:
      db.session.close()

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

    search_term = request.form.get('search_term', '')

    # find all artists matching search term
    # including partial match and case-insensitive
    artists = Artist.query.filter(Artist.name.ilike(f'%{search_term}%')).all()

    response = {
        "count": len(artists),
        "data": []
    }

    # for all matching artists, get num of upcoming shows
    # and add data to reponse
    for artist in artists:
        num_upcoming_shows = 0

        shows = Show.query.filter_by(artist_id=artist.id).all()

        for show in shows:
            if show.start_time > datetime.now():
                num_upcoming_shows += 1

        response['data'].append({
            "id": artist.id,
            "name": artist.name,
            "num_upcoming_shows": num_upcoming_shows,
        })

    # return reponse with matching search results
    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  
    # get artist by id
    artist = Artist.query.filter_by(id=artist_id).first()

    # get all shows matching artist id
    shows = Show.query.filter_by(artist_id=artist_id).all()

    # returns upcoming shows
    def upcoming_shows():
        upcoming = []

        # if the show is upcoming, add to upcoming
        for show in shows:
            if show.start_time > datetime.now():
                upcoming.append({
                    "venue_id": show.venue_id,
                    "venue_name": Venue.query.filter_by(id=show.venue_id).first().name,
                    "venue_image_link": Venue.query.filter_by(id=show.venue_id).first().image_link,
                    "start_time": format_datetime(str(show.start_time))
                })
        return upcoming

    # returns past shows
    def past_shows():
        past = []

        # if show is in past, add to past
        for show in shows:
            if show.start_time < datetime.now():
                past.append({
                    "venue_id": show.venue_id,
                    "venue_name": Venue.query.filter_by(id=show.venue_id).first().name,
                    "venue_image_link": Venue.query.filter_by(id=show.venue_id).first().image_link,
                    "start_time": format_datetime(str(show.start_time))
                })
        return past

    # data for given artist
    data = {
        "id": artist.id,
        "name": artist.name,
        "genres": artist.genres,
        "city": artist.city,
        "state": artist.state,
        "phone": artist.phone,
        "website_link": artist.website_link,
        "facebook_link": artist.facebook_link,
        "seeking_venue": artist.seeking_venue,
        "seeking_description": artist.seeking_description,
        "image_link": artist.image_link,
        "past_shows": past_shows(),
        "upcoming_shows": upcoming_shows(),
        "past_shows_count": len(past_shows()),
        "upcoming_shows_count": len(upcoming_shows()),
    }

    # return artist page with data
    return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  
  artist= Artist.query.get(artist_id)

  

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
  
  form = ArtistForm(request.form)
  
  if True:
    try:
      artist = Artist.query.get(artist_id)
      artist.name = form.name.data
      artist.city = form.city.data
      artist.state = form.state.data
      artist.phone = form.phone.data
      artist.genres = ','.join(form.genres.data)
      artist.facebook_link = form.facebook_link.data
      artist.image_link = form.image_link.data
      artist.website_link = form.website_link.data
      artist.seeking_venue = form.seeking_venue.data
      artist.seeking_description = form.seeking_description.data

      db.session.commit()

    except Exception:
      error = True
      db.session.rollback()
      print(sys.exc_info())
    
    finally:
      db.session.close()

    if not error: 
      flash('Artist '+ request.form['name'] + ' was successfully updated!')

    if error:
      flash('An error occured. Artist '+ request.form['name'] + ' could not be updated.')


    # TODO: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes

    return redirect(url_for('show_artist', artist_id=artist_id))



@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  
  
  form = VenueForm()

  venue= Venue.query.get(venue_id)

  form.name.data = venue.name
  form.city.data = venue.city
  form.state.data = venue.state
  form.address.data = venue.address
  form.phone.data = venue.phone
  form.genres.data = venue.genres
  form.facebook_link.data = venue.facebook_link
  form.image_link.data = venue.image_link
  form.website_link.data = venue.website_link
  form.seeking_talent.data = venue.seeking_talent
  form.seeking_description.data = venue.seeking_description

  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  error = False

  form = VenueForm(request.form)

  if True:
    try:
      venue = Venue.query.get(venue_id)
      venue.name = form.name.data
      venue.city = form.city.data
      venue.state = form.state.data
      venue.phone = form.phone.data
      venue.address = form.address.data
      venue.genres = ','.join(form.genres.data)
      venue.facebook_link = form.facebook_link.data
      venue.image_link = form.image_link.data
      venue.website_link = form.website_link.data
      venue.seeking_talent = form.seeking_talent.data
      venue.seeking_description = form.seeking_description.data
        
      db.session.commit()

    except Exception:
      error = True
      db.session.rollback()
      print(sys.exc_info())

    finally:
      db.session.close()

    if not error:
      flash('Venue '+ request.form['name'] + ' was successfully updated!')

    if error:
      flash('An error occured. Venue '+ request.form['name'] + ' could not be updated')


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

  if True:

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

   data = []

    # get venue and artist information for each show
   for show in shows:
        data.append({
            "venue_id": show.venue_id,
            "venue_name": Venue.query.filter_by(id=show.venue_id).first().name,
            "artist_id": show.artist_id,
            "artist_name": Artist.query.filter_by(id=show.artist_id).first().name,
            "artist_image_link": Artist.query.filter_by(id=show.artist_id).first().image_link,
            "start_time": format_datetime(str(show.start_time))
        })

    # return shows page with show data
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
  form = ShowForm(request.form)

  if True:
     try:
      show = Show(
      artist_id = form.artist_id.data,
      venue_id = form.venue_id.data,
      start_time = form.start_time.data
    )

      db.session.add(show)
      db.session.commit()
     except:
      db.session.rollback()
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
