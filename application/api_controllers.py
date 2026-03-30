"""
File:    api_controllers.py
Author: Pranathi Ayyadevara
Summary of File:
	This file contains code which has the controllers used for apis
"""

from .models import *
from .api_exceptions import *
from .utilities import*
from flask import request
from flask_restful import Resource, fields, marshal_with, reqparse
import matplotlib
matplotlib.use('Agg')
import base64

section_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
name = db.Column(db.String, unique = True, nullable = False)
date = db.Column(db.DateTime, default=datetime.utcnow)
description = db.Column(db.Text)

# Section REST methods
section_output = {
	"section_id": fields.Integer,
	"name": fields.String,
	"date": fields.DateTime,
    "description": fields.String
}

section_parser = reqparse.RequestParser()
section_parser.add_argument("name", type = str, required=True)
section_parser.add_argument("date", type = datetime, required=True)
section_parser.add_argument("description", type = str, required=True)

class SectionAPI(Resource):
	@marshal_with(section_output)
	def get(self, section_id):
		section = Sections.query.get(section_id)
		return section
	
	@marshal_with(section_output)
	def put(self, section_id):
		section = Sections.query.get(section_id)

		if section is None:
			raise NotFoundError(status_code=404)
		name = request.json["name"]
		description = request.json["description"]
		print(name, description, section_id)
		if not section:
			raise ValidationError(status_code = 400, error_code = "SECTION003", error_message = "Section ID doesn't exist")
		try:
			if not ((name is None) or (name == "")):
				print("Name updated")
				section.name = name
			if not ((description is None) or (description == "")):
				print("Description updated")
				section.description = description
			date = datetime.now()
			section.date = date
			db.session.flush()
		except Exception as e:
			print(e)
			db.session.rollback()
		finally:
			db.session.commit()
		return section

	@marshal_with(section_output)
	def post(self):
		print("Post")
		name = request.json["name"]
		description = request.json["description"]
		date = datetime.now()
		print("Post")
		print(name, date, description)

		if (name is None) or (name == ""):
			raise ValidationError(status_code=400, error_code="SECTION001", error_message="Section Name is required")

		if (description is None) or (description == ""):
			raise ValidationError(status_code=400, error_code="SECTION002", error_message="Section Description is required")
		try:
			section = Sections(name = name, date = date, description = description)
			db.session.add(section)
			db.session.flush()
		except Exception as e:
			print(e)
			db.session.rollback()
		finally:
			print("Finally")
			db.session.commit()
		return section,201

	
	@marshal_with(section_output)
	def delete(self, section_id):
		section = Sections.query.get(section_id)
		books = Books.query.filter_by(section_id = section_id).all()
		try:
			if section is None:
				raise NotFoundError(status_code=404)
			print("Books query worked")
			for book in books:
				print("Deleting", book.title)
				db.session.delete(book)
			db.session.delete(section)
			db.session.flush()
			print("Deleted")
		except Exception as e:
			print(e)
			db.session.rollback()
		finally:
			db.session.commit()

		return "", 200

class SectionsAPI(Resource):
	@marshal_with(section_output)
	def get(self):
		sections = Sections.query.all()
		return sections



# Book REST methods
book_output = {
	"book_id": fields.Integer,
	"title": fields.String,
	"author": fields.String,
	"pages": fields.Integer,
	"rating": fields.Integer,
	"isbn_no": fields.Integer,
	"datecreated": fields.DateTime,
	"lang": fields.String,
	"copies": fields.Integer,
	"availablecopies": fields.Integer,
    "description": fields.String,
	"section_id": fields.Integer
}

book_parser = reqparse.RequestParser()
book_parser.add_argument("title")
book_parser.add_argument("author")
book_parser.add_argument("pages")
book_parser.add_argument("rating")
book_parser.add_argument("isbn_no")
book_parser.add_argument("datecreated")
book_parser.add_argument("copies")
book_parser.add_argument("availablecopies")
book_parser.add_argument("description")
book_parser.add_argument("section_id")

class BookAPI(Resource):
	@marshal_with(book_output)
	def get(self, book_id):
		book = Books.query.filter_by(book_id = book_id).first()
		print(book)
		if book:
			return book
		else:
			raise NotFoundError(status_code=404)

	@marshal_with(book_output)
	def put(self, book_id):
		book = Books.query.get(book_id)
		borrowed = book.copies - book.availablecopies
		if book is None:
			raise NotFoundError(status_code=404)
		
		title = request.json["title"]
		print("Post")
		author = request.json["author"]
		pages = request.json["pages"]
		isbn_no = request.json["isbn_no"]
		lang = request.json["lang"]
		copies = request.json["copies"]
		description = request.json["description"]
		print("Post")
		
		try:
			if not ((title is None) or (title == "")):
				book.title = title
			if not ((author is None) or (author == "")):
				book.author = author
			if not ((pages is None) or (pages == "")):
				book.pages = pages
			if not ((isbn_no is None) or (isbn_no == "")):
				book.isbn_no = isbn_no
			if not ((lang is None) or (lang == "")):
				book.lang = lang
			if not ((copies is None) or (copies == "")):
				book.copies = copies
			if not ((copies is None) or (copies == "")):
				book.availablecopies = copies - borrowed
			if not ((description is None) or (description == "")):
				book.description = description
			db.session.flush()
			print("Check")
		except Exception as e:
			print(e)
			db.session.rollback()
		finally:
			db.session.commit()
		return book

	@marshal_with(book_output)
	def post(self):
		title = request.json["title"]
		author = request.json["author"]
		pages = request.json["pages"]
		isbn_no = request.json["isbn_no"]
		lang = request.json["lang"]
		copies = request.json["copies"]
		description = request.json["description"]
		section_id = request.json["section_id"]
		section = Sections.query.get(section_id)
		if section is None:
			raise NotFoundError(status_code=404)

		if (name is None) or (name == ""):
			raise ValidationError(status_code=400, error_code = "BOOK001", error_message = "Book title is required")
		if (author is None) or (author == ""):
			raise ValidationError(status_code=400, error_code = "BOOK002", error_message = "Book author is required")
		if (pages is None) or (pages == ""):
			raise ValidationError(status_code=400, error_code = "BOOK003", error_message = "Book pages is required")
		if (isbn_no is None) or (isbn_no == ""):
			raise ValidationError(status_code=400, error_code = "BOOK004", error_message = "Book isbn_no is required")
		if (lang is None) or (lang == ""):
			raise ValidationError(status_code=400, error_code = "BOOK005", error_message = "Book language is required")
		if (copies is None) or (copies == "") or (copies < 0):
			raise ValidationError(status_code=400, error_code = "BOOK006", error_message = "Book copies is required")
		if (description is None) or (description == ""):
			raise ValidationError(status_code=400, error_code = "BOOK007", error_message = "Book description is required")
		
		try:
			book = Books()
			book.title = title
			book.author = author
			book.pages = pages
			book.rating = 0
			book.isbn_no = isbn_no
			book.lang = lang
			book.copies = copies
			book.availablecopies = copies
			book.description = description
			book.section_id = section_id
			date = datetime.now()
			book.datecreated = date
			db.session.add(book)
			db.session.flush()
			print("Check")
		except Exception as e:
			print(e)
			db.session.rollback()
		finally:
			db.session.commit()
		return book
	
	@marshal_with(book_output)
	def delete(self, book_id):
		book = Books.query.get(book_id)
		try:
			if book is None:
				raise NotFoundError(status_code=404)
			db.session.delete(book)
			db.session.flush()
			print("Deleted")
		except Exception as e:
			print(e)
			db.session.rollback()
		finally:
			db.session.commit()

		return "", 200


class BooksAPI(Resource):
	@marshal_with(book_output)
	def get(self):
		books = Books.query.all()
		return books

section_parser = reqparse.RequestParser()
section_parser.add_argument("title")
section_parser.add_argument("author")
section_parser.add_argument("pages")
section_parser.add_argument("rating")
section_parser.add_argument("isbn_no")
section_parser.add_argument("datecreated")
section_parser.add_argument("copies")
section_parser.add_argument("availablecopies")
section_parser.add_argument("description")
section_parser.add_argument("section_id")

class GraphAPI(Resource):
	def get(self):
		admin = Users.query.filter_by(role = 2).first()
		create_stats(admin)
		with open('static/sections.png', 'rb') as image_file:
			sections = base64.b64encode(image_file.read()).decode('utf-8')
		with open('static/number_of_books.png', 'rb') as image_file:
			number_of_books = base64.b64encode(image_file.read()).decode('utf-8')
		with open('static/number_of_pages.png', 'rb') as image_file:
			number_of_pages = base64.b64encode(image_file.read()).decode('utf-8')
		with open('static/section_wise_copies.png', 'rb') as image_file:
			section_wise_copies = base64.b64encode(image_file.read()).decode('utf-8')
		response_data = {
			'sections': sections,
			'number_of_books': number_of_books,
			'number_of_pages': number_of_pages,
			'section_wise_copies': section_wise_copies
        }
		return response_data
