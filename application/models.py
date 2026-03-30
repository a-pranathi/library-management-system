"""
File:    models.py
Author: Pranathi Ayyadevara
Summary of File:
	This file contains code which has the models for the entities in the database
"""

from datetime import datetime
from .database import db
from flask_login import UserMixin

class Books(db.Model):
    book_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    title = db.Column(db.String, nullable = False)
    author = db.Column(db.String, nullable = False)
    pages = db.Column(db.Integer, nullable = False)
    rating = db.Column(db.Integer)
    isbn_no = db.Column(db.Integer, nullable = False)
    datecreated = db.Column(db.DateTime, default=datetime.now) 
    lang = db.Column(db.String, nullable = False)
    copies = db.Column(db.Integer, nullable = False)
    availablecopies = db.Column(db.Integer, nullable = False)
    description = db.Column(db.Text)
    filename = db.Column(db.String, nullable = False)
    price= db.Column(db.Integer, nullable = False)
    section_id = db.Column(db.Integer, db.ForeignKey("sections.section_id"), nullable = False)

class Sections(db.Model):
    section_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String, unique = True, nullable = False)
    date = db.Column(db.DateTime, default=datetime.now)
    description = db.Column(db.Text)

class Users(db.Model, UserMixin):
    user_id = db.Column(db.Integer(), autoincrement=True, primary_key=True)
    username = db.Column(db.String(), unique = True, nullable = False)
    password = db.Column(db.String(), nullable = False)
    name = db.Column(db.String(), nullable = False)
    role = db.Column(db.Integer, db.ForeignKey("roles.role_id"), nullable = False, default = 3)
    date = db.Column(db.DateTime(), default=datetime.now)
    def get_id(self):
        return (self.user_id)

class Roles(db.Model):
    role_id =  db.Column(db.Integer(), autoincrement=True, primary_key=True)
    role_name = db.Column(db.String(), unique = True, nullable = False)

class Checkouts(db.Model):
    checkout_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable = False)
    book_id = db.Column(db.Integer, db.ForeignKey("books.book_id"), nullable = False)
    date_requested = db.Column(db.DateTime, default=datetime.now)
    date_issued = db.Column(db.DateTime)
    date_returned = db.Column(db.DateTime)
    date_to_be_returned = db.Column(db.DateTime)
    date_rejected = db.Column(db.DateTime)
    date_revoked = db.Column(db.DateTime)
    date_purchased = db.Column(db.DateTime)
    status = db.Column(db.String(), nullable = False)

class Reviews(db.Model):
    review_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), nullable = False)
    book_id = db.Column(db.Integer, db.ForeignKey("books.book_id"), nullable = False)
    date_reviewed = db.Column(db.DateTime, default=datetime.now)
    rating = db.Column(db.Integer(), nullable = False)
    review = db.Column(db.Text())
