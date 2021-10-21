from sqlalchemy.orm import backref
from app import db

class Venue(db.Model):
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String())
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String())
    genres = db.relationship('Venue_gen', back_populates='gen', cascade="all, delete-orphan")
    shows = db.relationship('Show', backref='venue')

class Venue_gen(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    genre = db.Column(db.String())
    venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'))
    gen = db.relationship('Venue', back_populates='genres')

    def __repr__(self):
        return f'{self.genre}'

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
    website_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String())
    genres = db.relationship('Artist_gen', back_populates='gen', cascade="all, delete-orphan")
    shows = db.relationship('Show', backref='artist')

class Artist_gen(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    genre = db.Column(db.String())
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'))
    gen = db.relationship('Artist', back_populates='genres')

    def __repr__(self):
        return f'{self.genre}'    

class Show(db.Model):
    __tablename__ = 'shows'

    id = db.Column(db.Integer, primary_key=True)
    event_dt = db.Column(db.String(20))
    venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'))
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'))
