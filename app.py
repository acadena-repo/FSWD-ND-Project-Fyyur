#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
from os import name
from datetime import datetime as dt
from typing import Type
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from models import db, Venue, Artist, Show, Venue_gen, Artist_gen
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)
#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#
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
  i = 0
  data = []
  all_venues = Venue.query.order_by(Venue.city).all()

  while i < len(all_venues):
    venue = all_venues[i]
    city = venue.city
    state = venue.state

    venue_by_city = Venue.query.filter(Venue.city==city).all()
    i += len(venue_by_city)

    data_by_city = {}
    data_by_city['city'] = city
    data_by_city['state'] = state
    data_by_city['venues'] = []

    for v in venue_by_city:
      data_by_city['venues'].append({'id':v.id,'name':v.name})

    data.append(data_by_city)

  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  term = '%'+request.form.get("search_term")+'%'
  found_venues = Venue.query.filter(Venue.name.ilike(term)).all()
  response = {}
  response['count'] = len(found_venues)
  response['data'] = []

  for v in found_venues:
    response['data'].append({'id':v.id, 'name':v.name})

  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  dt_now = dt.now().strftime("%Y-%m-%d %H:%M:%S")
  pst = 0
  nxt = 0
  venue = Venue.query.get(venue_id)
  all_shows = Show.query.filter_by(venue_id = str(venue_id))
  past_shows = []
  next_shows = []

  for show in all_shows:
    artist = Artist.query.get(show.artist_id)
    if show.event_dt > dt_now:
      next_shows.append({'artist_id':artist.id, 'artist_name':artist.name,
      'artist_image_link':artist.image_link, 'start_time':show.event_dt})
      nxt += 1
    else:
      past_shows.append({'artist_id':artist.id, 'artist_name':artist.name,
      'artist_image_link':artist.image_link, 'start_time':show.event_dt})
      pst += 1

    data = {'id':venue.id, 'name':venue.name, 'genres':venue.genres, 'address':venue.address,
    'city':venue.city, 'state':venue.state, 'phone':venue.phone, 'website':venue.website_link, 'facebook_link':venue.facebook_link,
    'seeking_talent':venue.seeking_talent, 'seeking_description':venue.seeking_description, 'image_link':venue.image_link,
    'past_shows':past_shows, 'past_shows_count':pst, 'upcoming_shows':next_shows, 'upcoming_shows_count':nxt}

  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()

  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():

  try:
    new_venue = Venue()
    new_venue.name = request.form.get("name")
    new_venue.city = request.form.get("city")
    new_venue.state = request.form.get("state")
    new_venue.address = request.form.get("address")
    new_venue.phone = request.form.get("phone")
    new_venue.image_link = request.form.get("image_link")
    new_venue.facebook_link = request.form.get("facebook_link")
    new_venue.website_link = request.form.get("website_link")
    new_venue.seeking_talent = True if request.form.get("seeking_talent") == 'y' else False
    new_venue.seeking_description = request.form.get("seeking_description")
    db.session.add(new_venue)
    db.session.flush()

    new_gen = [Venue_gen() for i in range(len(request.form.getlist("genres")))]
    for i, g in enumerate(request.form.getlist("genres")):
      new_gen[i].venue_id = new_venue.id
      new_gen[i].genre = g
      db.session.add(new_gen[i])

    db.session.commit()    
    # on successful db insert, flash success
    flash('Venue ' + request.form.get("name") + ' was successfully listed!')

    return render_template('pages/home.html')

  except Exception as e:
    # on unsuccessful db insert, flash an error
    flash('An error occurred during insertion ' + str(e) + ' Venue could not be listed.')

    return render_template('pages/home.html')

@app.route('/venues/<venue_id>/delete', methods=['GET'])
def delete_venue(venue_id):

  try:
    del_venue = Venue.query.get(venue_id)
    db.session.delete(del_venue)
    db.session.commit()

    flash('Venue ' + del_venue.name + ' was successfully deleted!')
    return render_template('pages/home.html')

  except Exception as e:
    flash('An error occurred during operation ' + str(e) + ' Venue could not be deleted.')
    return render_template('pages/home.html')

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  data = []
  all_artist = Artist.query.order_by(Artist.name).all()

  for a in all_artist:
    data.append({'id':a.id, 'name':a.name})

  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  term = '%'+request.form.get("search_term")+'%'
  found_artist = Artist.query.filter(Artist.name.ilike(term)).all()
  response = {}
  response['count'] = len(found_artist)
  response['data'] = []

  for a in found_artist:
    response['data'].append({'id':a.id, 'name':a.name})

  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  dt_now = dt.now().strftime("%Y-%m-%d %H:%M:%S")
  pst = 0
  nxt = 0
  artist = Artist.query.get(artist_id)
  all_shows = Show.query.filter_by(artist_id = str(artist_id))
  past_shows = []
  next_shows = []

  for show in all_shows:
    venue = Venue.query.get(show.venue_id)
    if show.event_dt > dt_now:
      next_shows.append({'venue_id':venue.id, 'venue_name':venue.name,
      'venue_image_link':venue.image_link, 'start_time':show.event_dt})
      nxt += 1
    else:
      past_shows.append({'venue_id':venue.id, 'venue_name':venue.name,
      'venue_image_link':venue.image_link, 'start_time':show.event_dt})
      pst += 1

    data = {'id':artist.id, 'name':artist.name, 'genres':artist.genres, 'city':artist.city, 'state':artist.state, 'phone':artist.phone, 
    'website':artist.website_link, 'facebook_link':artist.facebook_link, 'seeking_venue':artist.seeking_venue, 
    'seeking_description':artist.seeking_description, 'image_link':artist.image_link,
    'past_shows':past_shows, 'past_shows_count':pst, 'upcoming_shows':next_shows, 'upcoming_shows_count':nxt}

  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  artist = Artist.query.get(artist_id)
  form = ArtistForm()

  gens = []
  for g in artist.genres:
    gens.append(f'{g}')

  form.name.data = artist.name
  form.city.data = artist.city
  form.state.data = artist.state
  form.phone.data = artist.phone
  form.genres.data = gens
  form.image_link.data = artist.image_link
  form.facebook_link.data = artist.facebook_link
  form.website_link.data = artist.website_link
  form.seeking_venue.data = True if artist.seeking_venue else False
  form.seeking_description.data = artist.seeking_description

  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  artist = Artist.query.get(artist_id)

  artist.name = request.form.get("name")
  artist.city = request.form.get("city")
  artist.state = request.form.get("state")
  artist.phone = request.form.get("phone")
  artist.image_link = request.form.get("image_link")
  artist.facebook_link = request.form.get("facebook_link")
  artist.website_link = request.form.get("website_link")
  artist.seeking_talent = True if request.form.get("seeking_talent") == 'y' else False
  artist.seeking_description = request.form.get("seeking_description")
  
  db.session.commit()

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  venue = Venue.query.get(venue_id)
  form = VenueForm()

  gens = []
  for g in venue.genres:
    gens.append(f'{g}')

  form.name.data = venue.name
  form.city.data = venue.city
  form.state.data = venue.state
  form.address.data = venue.address
  form.phone.data = venue.phone
  form.genres.data = gens
  form.image_link.data = venue.image_link
  form.facebook_link.data = venue.facebook_link
  form.website_link.data = venue.website_link
  form.seeking_talent.data = True if venue.seeking_talent else False
  form.seeking_description.data = venue.seeking_description

  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  venue = Venue.query.get(venue_id)

  venue.name = request.form.get("name")
  venue.city = request.form.get("city")
  venue.state = request.form.get("state")
  venue.address = request.form.get("address")
  venue.phone = request.form.get("phone")
  venue.image_link = request.form.get("image_link")
  venue.facebook_link = request.form.get("facebook_link")
  venue.website_link = request.form.get("website_link")
  venue.seeking_talent = True if request.form.get("seeking_talent") == 'y' else False
  venue.seeking_description = request.form.get("seeking_description")
  
  db.session.commit()

  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():

  try:
    new_artist = Artist()
    new_artist.name = request.form.get("name")
    new_artist.city = request.form.get("city")
    new_artist.state = request.form.get("state")
    new_artist.phone = request.form.get("phone")
    new_artist.image_link = request.form.get("image_link")
    new_artist.facebook_link = request.form.get("facebook_link")
    new_artist.website_link = request.form.get("website_link")
    new_artist.seeking_venue = True if request.form.get("seeking_venue") == 'y' else False
    new_artist.seeking_description = request.form.get("seeking_description")
    db.session.add(new_artist)
    db.session.flush()

    new_gen = [Artist_gen() for i in range(len(request.form.getlist("genres")))]
    for i, g in enumerate(request.form.getlist("genres")):
      new_gen[i].artist_id = new_artist.id
      new_gen[i].genre = g
      db.session.add(new_gen[i])

    db.session.commit()    
    # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully listed!')

    return render_template('pages/home.html')

  except Exception as e:
    # on unsuccessful db insert, flash an error
    flash('An error occurred during insertion ' + str(e) + ' Artist could not be listed.')

    return render_template('pages/home.html')

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  data = []
  all_shows = Show.query.all()

  for show in all_shows:
    artist = Artist.query.get(show.artist_id)
    venue = Venue.query.get(show.venue_id)
    data.append({'venue_id':venue.id, 'venue_name':venue.name, 'artist_id':artist.id, 'artist_name':artist.name,
    "artist_image_link":artist.image_link, "start_time":show.event_dt})

  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():

  try:
    new_show = Show()
    new_show.artist_id = request.form.get("artist_id")
    new_show.venue_id = request.form.get("venue_id")
    new_show.event_dt = request.form.get("start_time")
    db.session.add(new_show)

    db.session.commit()    
    # on successful db insert, flash success
    flash('Show was successfully listed!')

    return render_template('pages/home.html')

  except Exception as e:
    # on unsuccessful db insert, flash an error
    flash('An error occurred during insertion ' + str(e) + ' Show could not be listed.')

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
