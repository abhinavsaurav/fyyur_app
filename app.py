#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, jsonify
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
import config, sys
from flask_migrate import Migrate
from datetime import datetime
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

# TODO: connect to a local postgresql database
app.config['SQLALCHEMY_DATABASE_URI']=config.SQLALCHEMY_DATABASE_URI
migrate= Migrate(app,db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    
    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    
    genres=db.Column(db.String(120))    
    shows=db.relationship('Show',backref='venue',passive_deletes=True,lazy=True)

class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    
    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    genres=db.Column(db.String(120))
    shows=db.relationship('Show',backref='artist',passive_deletes=True,lazy=True)
    
# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class Show(db.Model):
    __tablename__= 'shows'
    venue_id=db.Column(db.Integer, db.ForeignKey('venue.id',ondelete='CASCADE'), primary_key=True, nullable=False)
    artist_id=db.Column(db.Integer, db.ForeignKey('artist.id',ondelete='CASCADE'), primary_key=True, nullable=False)
    start_time=db.Column(db.DateTime, primary_key=True, nullable= False)
    
    
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
    venues = Venue.query.all()
    data=[]
    for venue in venues:
      currentTime= datetime.utcnow()
      num_shows = Show.query.filter(Show.venue_id == Venue.id, Show.start_time > currentTime).count()
      dataobj={
        "city":venue.city,
        "state":venue.state,
        "venues":[{
          "id":venue.id,
          "name":venue.name,
          "num_upcoming_shows":num_shows
        }]
      }
      data.append(dataobj)
   
    return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_term=request.form.get('search_term')
  search= Venue.query.filter(Venue.name.ilike('%{0}%'.format(search_term)))
  currentTime=datetime.utcnow()
  
  data=[]
  for srch in search:
    ushows= db.session.query(Artist,Show, Venue).join(Show,Artist.id==Show.artist_id).join(Venue,Venue.id==Show.venue_id).filter(Venue.id== srch.id, Show.start_time>currentTime).all()
    dataobj={
      "id":srch.id,
      "name":srch.name,
      "num_upcoming_shows":len(ushows)
    }
    data.append(dataobj)
  response={
    "count": search.count(),
    "data": data
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  data=[]
  venue= Venue.query.filter_by(id=venue_id).first_or_404()
  currentTime=datetime.utcnow()
  pshows= db.session.query(Artist,Show, Venue).join(Show,Artist.id==Show.artist_id).join(Venue,Venue.id==Show.venue_id).filter(Venue.id== venue_id, Show.start_time<currentTime).all()
  ushows= db.session.query(Artist,Show, Venue).join(Show,Artist.id==Show.artist_id).join(Venue,Venue.id==Show.venue_id).filter(Venue.id== venue_id, Show.start_time>currentTime).all()
  past_shows=[]
  upcoming_shows=[]
  for show in pshows:
    showObj={
      "artist_id":show.Artist.id,
      "artist_name":show.Artist.name,
      "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
      "start_time":str(show.Show.start_time)
    }
    past_shows.append(showObj)
  for show in ushows:
    showObj={
      "artist_id":show.Artist.id,
      "artist_name":show.Artist.name,
      "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
      "start_time":str(show.Show.start_time)
    }
    upcoming_shows.append(showObj)
  
  data={
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": "https://www.dummyWebsite.com",
    "facebook_link": venue.facebook_link,
    # "seeking_talent": True,
    # "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    "image_link": venue.image_link,
    "past_shows":past_shows, 
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(pshows),
    "upcoming_shows_count": len(upcoming_shows),
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
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  try:
    name=request.form.get('name','')
    city = request.form.get('city')
    state = request.form.get('state')
    address = request.form.get('address')
    phone = request.form.get('phone')
    genres = request.form.get('genres')
    facebook_link = request.form.get('facebook_link')
    
    venue = Venue(name=name,city=city, state=state, address=address,phone=phone,genres=genres, facebook_link=facebook_link)
    db.session.add(venue)
    db.session.commit()
  except:
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
    
  
  # on successful db insert, flash success
  flash('Venue ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  try:
      venue=Venue.query.get(venue_id)
      db.session.delete(venue)
      db.session.commit()
  except :
      db.session.rollback()
      print(sys.exc_info())
  finally:
      db.session.close()
  return render_template('pages/home.html')
  
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  data=[]
  artists= Artist.query.all()
  for artist in artists:
    dataobj={
      "id":artist.id,
      "name":artist.name
    }
    data.append(dataobj) 
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_term=request.form.get('search_term')
  search= Artist.query.filter(Artist.name.ilike('%{0}%'.format(search_term)))
  currentTime=datetime.utcnow()
  data=[]
  for srch in search:
    ushows= db.session.query(Artist,Show, Venue).join(Show,Artist.id==Show.artist_id).join(Venue,Venue.id==Show.venue_id).filter(Venue.id== srch.id, Show.start_time>currentTime).all()
    dataobj={
      "id":srch.id,
      "name":srch.name,
      "num_upcoming_shows":len(ushows)
    }
    data.append(dataobj)
  response={
    "count": search.count(),
    "data": data
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  artist= Artist.query.filter_by(id=artist_id).first_or_404()
  currentTime=datetime.utcnow()
  pshows= db.session.query(Artist,Show, Venue).join(Show,Artist.id==Show.artist_id).join(Venue,Venue.id==Show.venue_id).filter(Artist.id==artist_id, Show.start_time<currentTime).all()
  ushows= db.session.query(Artist,Show, Venue).join(Show,Artist.id==Show.artist_id).join(Venue,Venue.id==Show.venue_id).filter(Artist.id==artist_id, Show.start_time>currentTime).all()
  past_shows=[]
  upcoming_shows=[]
  for show in pshows:
    showObj={
      "venue_id": show.Venue.id,
      "venue_name": show.Venue.name,
      "venue_image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
      "start_time": str(show.Show.start_time)
    }
    past_shows.append(showObj)
  for show in ushows:
    showObj={
      "venue_id": show.Venue.id,
      "venue_name": show.Venue.name,
      "venue_image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
      "start_time": str(show.Show.start_time)
    }
    upcoming_shows.append(showObj)
  
  
  data={
    "id": artist.id,
    "name": artist.name,
    "genres":artist.genres,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    # "website": "https://www.gunsnpetalsband.com",
    "facebook_link": artist.facebook_link,
    # "seeking_venue": True,
    # "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
    "image_link": artist.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows),
  }
  
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artists=Artist.query.filter_by(id=artist_id).first()
  artist={
    "id": artists.id,
    "name": artists.name,
    "genres": artists.genres,
    "city": artists.city,
    "state": artists.state,
    "phone": artists.phone,
    # "website": "https://www.gunsnpetalsband.com",
    "facebook_link": artists.facebook_link,
    # "seeking_venue": True,
    # "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
    "image_link": artists.image_link
  }
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  try:
    name=request.form.get('name','')
    city = request.form.get('city')
    state = request.form.get('state')
    phone = request.form.get('phone')
    genres = request.form.get('genres')
    facebook_link = request.form.get('facebook_link')
    
    artist=Artist.query.get(artist_id)
    artist.name=name
    artist.city=city
    artist.state=state
    artist.phone=phone
    artist.genres=genres
    artist.facebook_link=facebook_link
    db.session.commit()
  except:
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()


  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venues = Venue.query.filter_by(id=venue_id).first()
  venue={
    "id": venues.id,
    "name": venues.name,
    "genres": venues.genres,
    "address": venues.address,
    "city": venues.city,
    "state": venues.state,
    "phone": venues.phone,
    # "website": "https://www.themusicalhop.com",
    "facebook_link": venues.facebook_link,
    # "seeking_talent": True,
    # "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    "image_link": venues.image_link
  }
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  try:
    name=request.form.get('name','')
    city = request.form.get('city')
    state = request.form.get('state')
    address = request.form.get('address')
    phone = request.form.get('phone')
    genres = request.form.get('genres')
    facebook_link = request.form.get('facebook_link')
    
    venue = Venue.query.get(venue_id)
    venue.name=name
    venue.city=city
    venue.state=state
    venue.address=address
    venue.phone=phone
    venue.genres=genres
    venue.facebook_link=facebook_link
    db.session.commit()
  except:
    db.session.rollback()
    print(sys.exc_info())
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
  try:
    name=request.form.get('name','')
    city = request.form.get('city')
    state = request.form.get('state')
    phone = request.form.get('phone')
    genres = request.form.get('genres')
    facebook_link = request.form.get('facebook_link')
    
    artist = Artist(name=name,city=city, state=state,phone=phone,genres=genres, facebook_link=facebook_link)
    db.session.add(artist)
    db.session.commit()
  except:
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  
  # on successful db insert, flash success
  flash('Artist ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  data = []
  shows = Show.query.join(Venue, Show.venue_id == Venue.id).join(
      Artist, Artist.id == Show.artist_id).all()
  for show in shows:
    print(show.artist.name)
    showObj = {"venue_id": show.venue_id,
    "venue_name": show.venue.name,
    "artist_id": show.artist_id,
    "artist_name": show.artist.name,
    # "artist_image_link": show.artist.image_link,
    "start_time": str(show.start_time)
    }
    data.append(showObj)
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
  try:  
    artist_id = request.form.get('artist_id')
    venue_id= request.form.get('venue_id')
    start_time = request.form.get('start_time')
    show = Show(artist_id=artist_id,venue_id=venue_id, start_time=start_time)
    db.session.add(show)
    db.session.commit()
  except:
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  # on successful db insert, flash success
  flash('Show was successfully listed!')
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
