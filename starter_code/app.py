#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import logging
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, abort
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
import sys
from models import db, Artist, Venue, Show
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)

migrate = Migrate(app, db)

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
  data = []
  venues = Venue.query.all()
  
  cities_and_states = set()
  
  for venue in venues:
    cities_and_states.add((venue.city, venue.state))
  for item in cities_and_states:
    data.append({
       'city': item[0],
       'state': item[1],
       'venues': []
    })
  for venue in venues:
    num_upcoming_shows = 0

    shows = Show.query.filter_by(venue_id=venue.id).all()
    for show in shows:
      if show.start_time > datetime.now():
        num_upcoming_shows += 1

    for venue_location in data:
      if venue.state == venue_location['state'] and venue.city == venue_location['city']:
        venue_location['venues'].append({
          'id': venue.id,
          'name': venue.name,
          'num_upcoming_shows': num_upcoming_shows
        })
  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  search_term = request.form.get('search_term', None)
  venues = Venue.query.filter(Venue.name.ilike("%{}%".format(search_term))).all()
  venues_count = len(venues)
  
  response={
    "count": venues_count,
    "data": [venue.display_venue() for venue in venues]
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  venue = Venue.query.get_or_404(venue_id)

  past_shows = []
  upcoming_shows = []

  for show in venue.shows:
      data_shows = {
        'artist_id': show.artist_id,
        'artist_name': show.artist.name,
        'artist_image_link': show.artist.image_link,
        'start_time': format_datetime(str(show.start_time))
        }
      if show.start_time <= datetime.now():
        past_shows.append(data_shows)
      else:
        upcoming_shows.append(data_shows)

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
    "seeking_description":venue.seeking_description,
    "image_link": venue.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows)
  }

  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  form = VenueForm(request.form)
  error = False
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
    if (venue.name, venue.city, venue.state, venue.address, venue.genres, venue.seeking_talent) == None:
            abort(422)
    else:
      db.session.add(venue)
      db.session.commit()
  except:
    error = True
    db.session.rollback()
  finally:
    db.session.close()
    if error:
      flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
    else:
      flash('Venue ' + request.form['name'] + ' was successfully listed!')
    return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  error = False
  try:
    venue = Venue.query.get(venue_id)
    shows = Show.query.filter_by(venue_id=venue_id).all()
    venue_name = venue.name

    if shows is None:
      db.session.delete(venue)
    else:
      for show in shows:
        db.session.delete(show)
      db.session.delete(venue)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
  finally:
    db.session.close()
    if error:
      flash('Error. Venue ' + venue_name + ' has not been deleted.')
      return redirect(url_for('show_venue', venue_id=venue_id))
    else:
      flash('Venue ' + venue_name + ' has been deleted successfully.')
      return redirect(url_for('index'))

#  Update Venue
#  ----------------------------------------------------------------
@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()

  venue_to_edit = Venue.query.get(venue_id)

  if venue_to_edit is None:
    abort(404)

  venue = venue_to_edit.display_venue()
  form = VenueForm(data=venue)
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  form = VenueForm(request.form)
  error = False
  try:
    venue = Venue.query.get(venue_id)
    venue.name = form.name.data
    venue.genres = ','.join(form.genres.data)
    venue.address = form.address.data
    venue.city = form.city.data
    venue.state = form.state.data
    venue.phone = form.phone.data
    venue.website_link = form.website_link.data
    venue.facebook_link = form.facebook_link.data
    venue.image_link = form.image_link.data
    venue.seeking_talent = form.seeking_talent.data
    venue.seeking_description = form.seeking_description.data

    if (venue.name, venue.city, venue.state, venue.address, venue.genres, venue.seeking_talent) == None:
            abort(422)
    else:
      db.session.add(venue)
      db.session.commit()
  except Exception as e:
    error = True
    db.session.rollback()
    print(f'Exception "{e}" in update artist')
  finally:
    db.session.close()
    if error:
      flash('An error occurred. Venue ' + request.form['name'] + ' could not be updated.')
      print("Error in edit_venue_submission()")
      abort(500)
    else:
      flash('Venue ' + request.form['name'] + ' was successfully updated!')
      return redirect(url_for('show_venue', venue_id=venue_id))

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  artists = Artist.query.all()
  data = [artist.display_artist() for artist in artists]
  # TODO: replace with real data returned from querying the database
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  search_term = request.form.get('search_term', None)
  artists = Artist.query.filter(Artist.name.ilike("%{}%".format(search_term))).all() 
  artists_count = len(artists)
  response={
    "count": artists_count,
    "data": [artist.display_artist() for artist in artists]
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  artist = Artist.query.get_or_404(artist_id)

  past_shows = []
  upcoming_shows = []
  
  for show in artist.shows:
    data_shows = {
      'venue_id': show.venue_id,
      'venue_name': show.venue.name,
      'venue_image_link': show.venue.image_link,
      'start_time': format_datetime(str(show.start_time))
      }
    if show.start_time <= datetime.now():
      past_shows.append(data_shows)
    else:
      upcoming_shows.append(data_shows)
  
  data = {
    'id': artist.id,
    'name': artist.name,
    'genres': artist.genres,
    'city': artist.city,
    'state': artist.state,
    'phone': artist.phone,
    'facebook_link': artist.facebook_link,
    'website_link': artist.website_link,
    'image_link': artist.image_link,
    'past_shows': past_shows,
    'upcoming_shows': upcoming_shows,
    'past_shows_count': len(past_shows),
    'upcoming_shows_count': len(upcoming_shows)
  }
  
  return render_template('pages/show_artist.html', artist=data)

#  Update Artist
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()

  artist_to_edit = Artist.query.get(artist_id)

  if artist_to_edit is None:
    abort(404)

  artist = artist_to_edit.display_artist()
  form = ArtistForm(data=artist)
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  error = False
  form = ArtistForm(request.form)

  try:
    artist = Artist.query.get(artist_id)
    artist.name = form.name.data
    artist.city = form.city.data
    artist.state = form.state.data
    artist.phone = form.phone.data
    artist.seeking_venue = form.seeking_venue.data
    artist.seeking_description = form.seeking_description.data
    artist.image_link = form.image_link.data
    artist.website_link = form.website_link.data
    artist.facebook_link = form.facebook_link.data
    artist.genres = ','.join(form.genres.data)

    if (artist.name, artist.city, artist.state, artist.genres) == None:
            abort(422)
    else:
      db.session.add(artist)
      db.session.commit()

  except Exception as e:
      error = True
      db.session.rollback()
      print(f'Exception "{e}" in update artist')
  finally:
    db.session.close()
    if error:
      flash('An error occurred. Artist ' + request.form['name'] + ' could not be updated.')
      print("Error in edit_artist_submission()")
      abort(500)
    else:
      flash('Artist ' + request.form['name'] + ' was successfully updated!')
      return redirect(url_for('show_artist', artist_id=artist_id))


#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  error = False
  form = ArtistForm(request.form)
  try:
    artist = Artist(
      name = form.name.data,
      city = form.city.data,
      state = form.state.data,
      phone = form.phone.data,
      genres=','.join(form.genres.data),
      website_link = form.website_link.data,
      image_link = form.image_link.data,
      facebook_link = form.facebook_link.data,
      seeking_description = form.seeking_description.data
      )
    
    if (artist.name, artist.city, artist.state, artist.genres) == None:
            abort(422)
    else:
      db.session.add(artist)
      db.session.commit()
      flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except:
    error = True
    db.session.rollback()
    flash('An error occurred. ' + request.form['name'] + ' Artist could not be listed.')
    print(sys.exc_info())
  finally:
    db.session.close()
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  shows = Show.query.order_by(db.desc(Show.start_time))
  data =[]
  for show in shows:
    data.append({
      'venue_id': show.venue_id,
      'venue_name': show.venue.name,
      'artist_id': show.artist_id,
      'artist_name': show.artist.name,
      'artist_image_link': show.artist.image_link,
      'start_time': format_datetime(str(show.start_time))
    })
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  error = False
  form = ShowForm(request.form)
  try:
    show = Show(
      artist_id = form.artist_id.data,
      venue_id = form.venue_id.data,
      start_time = form.start_time.data
      )
    
    if (show.artist_id, show.venue_id, show.start_time) == None:
      abort(422)
    else:
       db.session.add(show)
       db.session.commit()
  except:
    error = True
    db.session.rollback()
  finally:
    db.session.close()
  if error:
    flash('An error occurred. Show could not be listed.')
  else:
    flash('Show was successfully listed!')
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
