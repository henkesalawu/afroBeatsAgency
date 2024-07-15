from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, String, Integer, Boolean
from flask_moment import Moment
from datetime import datetime


db = SQLAlchemy()

"""
Venue
"""
class Venue(db.Model):
    __tablename__ = 'venues'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    city = Column(String(120), nullable=False)
    state = Column(String(120), nullable=False)
    address = Column(String(120), nullable=False)
    genres = Column(String(120), nullable=False)
    phone = Column(String(120))
    image_link = Column(String(500))
    facebook_link = Column(String(120))
    website_link = Column(String(120))
    seeking_talent = Column(Boolean, default=False)
    seeking_description = Column(String(120))

    shows = db.relationship('Show', backref=db.backref('venue'), lazy='joined')

    def __repr__(self):
       return f'<Venue %r>' % self
    
    def display_venue(self):
      return {
        'id': self.id,
        'name': self.name,
        'genres': self.genres,
        'city': self.city,
        'state': self.state,
        'phone': self.phone,
        'address': self.address,
        'image_link': self.image_link,
        'facebook_link': self.facebook_link,
        'website_link': self.website_link,
        'seeking_talent': self.seeking_talent,
        'seeking description': self.seeking_description
      }

"""
Artist
"""
class Artist(db.Model):
    __tablename__ = 'artists'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    city = Column(String(120), nullable=False)
    state = Column(String(120), nullable=False)
    phone = Column(String(120))
    genres = Column(String(120), nullable=False)
    image_link = Column(String(500))
    facebook_link = Column(String(120))
    seeking_venue = Column(Boolean, default=False)
    website_link = Column(String(120))
    seeking_description = Column(String(120))

    shows = db.relationship('Show', backref=db.backref('artist'), lazy='joined')

    def __repr__(self):
        return f'<Artist %r>' % self

    def display_artist(self):
      return {
        'id': self.id,
        'name': self.name,
        'city': self.city,
        'state': self.state,
        'phone': self.phone,
        'genres': self.genres,
        'image_link': self.image_link,
        'website_link': self.website_link,
        'facebook_link': self.website_link,
        'seeking_venue': self.seeking_venue,
        'seeking_description': self.seeking_description
      }
    
class Show(db.Model):
    __tablename__ = 'shows'
    
    id = Column(Integer, primary_key=True)
    artist_id = Column(Integer, db.ForeignKey('artists.id'), nullable=False)
    venue_id = Column(Integer, db.ForeignKey('venues.id'), nullable=False)
    start_time = Column(db.DateTime, nullable=False)
    
    def __repr__(self):
       return f'<Show {self.id}, Artist {self.artist_id}, Venue {self.venue_id}>'