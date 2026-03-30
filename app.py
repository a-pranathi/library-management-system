"""
File:    app.py
Author1: Pranathi Ayyadevara
Roll No: 22f3001788
Course:  MAD 1 Project - LMS
Summary of File:
	This file contains code which creates and runs the main application
"""

import os
from flask import Flask
from application.database import db
from application.models import *
from application.utilities import *
from flask_restful import Api
from flask_login import LoginManager
from apscheduler.schedulers.background import BackgroundScheduler

current_dir = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(current_dir, 'data')
app = Flask(__name__)
app.debug = True
app.secret_key = 'the_secretest_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///library.sqlite3"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
login_manager = LoginManager()
login_manager.init_app(app)
db.init_app(app)
scheduler = BackgroundScheduler()
scheduler.add_job(update_book_status, 'interval', args=[app], seconds=10)
scheduler.start()
api = Api(app)

app.app_context().push()

from application.controllers import *
from application.api_controllers import *

api.add_resource(SectionAPI, "/api/section", "/api/section/<int:section_id>")
api.add_resource(SectionsAPI, "/api/sections")
api.add_resource(BookAPI, "/api/book", "/api/book/<int:book_id>")
api.add_resource(BooksAPI, "/api/books")
api.add_resource(GraphAPI, "/api/graphs")


if __name__ == "__main__":
    app.run()