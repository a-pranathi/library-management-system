"""
File:    utilities.py
Author: Pranathi Ayyadevara
Summary of File:
	This file contains code which has the  miscellaneous functions
"""

from .models import *
from sqlalchemy import asc
from flask import current_app as app
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np


issueDays = {"5 seconds": 5 ,"5 minutes": 5, "1 day" : 1, "5 days": 5, "1 week": 7, "2 weeks": 14}

def isAdmin(user):
    if user.role == 3:
        return False
    else:
        return True

def update_book_status(app):
    with app.app_context():
        issued_books = Checkouts.query.filter_by(status = "Issued").order_by(asc(Checkouts.date_to_be_returned)).all()
        for issued_book in issued_books:
            if issued_book.date_to_be_returned <= datetime.now():
                try:
                    date = datetime.now()
                    book = Books.query.get(issued_book.book_id)
                    book.availablecopies +=1
                    issued_book.status = "Returned"
                    issued_book.date_returned = date
                    db.session.flush()
                except Exception as e:
                    print(e)
                    db.session.rollback()
                finally:
                    db.session.commit()
            else:
                break

def create_stats(user):
    admin = isAdmin(user)
    if admin:
        plt.figure()
        books = Books.query.all()
        count = []
        for book in books:
            count.append(book.copies)
        binwidth = 2
        plt.hist(count, rwidth = 0.7, color='darkorchid', bins=range(min(count), max(count) + binwidth))
        plt.title("Number of Book")
        plt.savefig('static/number_of_books.png')

        plt.figure()
        section_names = Books.query.join(Sections, Sections.section_id == Books.section_id).add_columns(Sections.name).all()
        sections = []
        for bk in section_names:
            sections.append(bk.name)
        d={}
        for sec in sections:
            if sec in d:
                d[sec]+=1
            else:
                d[sec]=1
        def percentage(pct, data):
            absolute = int(pct / 100.*np.sum(data))
            return "{:.1f}%\n({:d} books)".format(pct, absolute)
        labels, values = [], []
        explode = []
        for i in d:
            labels.append(i)
            values.append(d[i])
            explode.append(.1)
        fig, ax = plt.subplots(figsize=(10, 7))
        wp = {'linewidth': 3, 'edgecolor': "black"}
        wedges, texts, autotexts = ax.pie(values, autopct=lambda pct: percentage(pct, values), explode = explode, labels=labels, shadow=True, startangle=90, wedgeprops=wp, textprops=dict(color="black"))
        ax.set(title="Section Distibution: ")
        plt.legend(title = "Sections: ")
        plt.savefig('static/sections.png')

        plt.figure()
        section_names, availablecopies, borrowedcopies = [], [], []
        sections = Sections.query.all()
        for section in sections:
            available_count, borrowed_count = 0, 0
            section_names.append(section.name)
            books = Books.query.filter_by(section_id = section.section_id).all()
            for book in books:
                available_count += book.availablecopies
                borrowed_count += (book.copies - book.availablecopies)
            availablecopies.append(available_count)
            borrowedcopies.append(borrowed_count)
        plt.bar(section_names, availablecopies, color='dodgerblue')
        plt.bar(section_names, borrowedcopies, bottom=availablecopies, color='darkorange')
        plt.xlabel("Sections")
        plt.ylabel("Number of Copies")
        plt.legend(["Available Copies", "Borrowed Copies"])
        plt.title("Section Wise Available Copies")
        plt.margins(x = 0.1, y = 1)
        plt.savefig('static/section_wise_copies.png')

        plt.figure()
        books = Books.query.all()
        count = []
        for book in books:
            count.append(book.pages)
        plt.hist(count, color='springgreen', rwidth = 0.7)
        plt.title("Number of Pages")
        plt.savefig('static/number_of_pages.png')
    else:
        books = Books.query.all()
        count = []
        for book in books:
            count.append(book.copies)
        binwidth = 2
        plt.hist(count, rwidth = 0.7, color='darkorchid', bins=range(min(count), max(count) + binwidth))
        plt.title("Number of Book")
        plt.savefig('static/number_of_books.png')

        plt.figure()
        section_names = Books.query.join(Sections, Sections.section_id == Books.section_id).add_columns(Sections.name).all()
        sections = []
        for bk in section_names:
            sections.append(bk.name)
        d={}
        for sec in sections:
            if sec in d:
                d[sec]+=1
            else:
                d[sec]=1
        def percentage(pct, data):
            absolute = int(pct / 100.*np.sum(data))
            return "{:.1f}%\n({:d} books)".format(pct, absolute)
        labels, values = [], []
        explode = []
        for i in d:
            labels.append(i)
            values.append(d[i])
            explode.append(.1)
        fig, ax = plt.subplots(figsize=(10, 7))
        wp = {'linewidth': 3, 'edgecolor': "black"}
        wedges, texts, autotexts = ax.pie(values, autopct=lambda pct: percentage(pct, values), explode = explode, labels=labels, shadow=True, startangle=90, wedgeprops=wp, textprops=dict(color="black"))
        ax.set(title="Section Distibution: ")
        plt.legend(title = "Sections: ")
        plt.savefig('static/sections.png')

        plt.figure()
        section_names, availablecopies, borrowedcopies = [], [], []
        sections = Sections.query.all()
        for section in sections:
            available_count, borrowed_count = 0, 0
            section_names.append(section.name)
            books = Books.query.filter_by(section_id = section.section_id).all()
            for book in books:
                available_count += book.availablecopies
                borrowed_count += (book.copies - book.availablecopies)
            availablecopies.append(available_count)
            borrowedcopies.append(borrowed_count)
        plt.bar(section_names, availablecopies, color='dodgerblue')
        plt.bar(section_names, borrowedcopies, bottom=availablecopies, color='darkorange')
        plt.xlabel("Sections")
        plt.ylabel("Number of Copies")
        plt.legend(["Available Copies", "Borrowed Copies"])
        plt.title("Section Wise Available Copies")
        plt.margins(x = 0.1, y = 1)
        plt.savefig('static/section_wise_copies.png')

        plt.figure()
        books = Books.query.all()
        count = []
        for book in books:
            count.append(book.pages)
        plt.hist(count, color='springgreen', rwidth = 0.7)
        plt.title("Number of Pages")
        plt.savefig('static/number_of_pages.png')
