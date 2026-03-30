"""
File:    api_exceptions.py
Author: Pranathi Ayyadevara
Summary of File:
	This file contains code which has the exceptions used for apis
"""

from .models import *
from flask import make_response
from flask.helpers import make_response
from werkzeug.exceptions import HTTPException, InternalServerError
import json

class NotFoundError(HTTPException):
	def __init__(self, status_code):
		self.response = make_response('', status_code)

class InternalServerError(HTTPException):
	def __init__(self, status_code):
		self.response = make_response('', status_code)

class BadRequestError(HTTPException):
	def __init__(self, status_code):
		self.response = make_response('', status_code)

class ValidationError(HTTPException):
	def __init__(self, status_code, error_code, error_message):
		message = {
			"error_code": error_code,
			"error_message": error_message
			}
		self.response = make_response(json.dumps(message), status_code)
