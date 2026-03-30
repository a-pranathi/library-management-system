"""
File:    controllers.py
Author: Pranathi Ayyadevara
Summary of File:
	This file contains code which has the controllers
"""

from .models import *
from .utilities import *
import os
from flask import redirect, render_template, request, url_for, abort, send_file
from flask import current_app as app
from app import login_manager
from flask_login import login_user, logout_user, current_user, login_required
from datetime import datetime, timedelta

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(APP_ROOT, 'data')


@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(user_id)

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect('/dashboard')
    else:
        return redirect('/login')

@app.route('/login', methods = ['GET', 'POST'])
def login():
    if request.method == "GET":
        return render_template("login.html")
    elif request.method == "POST":
        user_name = request.form.get("user_name")
        pass_word = request.form.get("pass")
        this_user = Users.query.filter_by(username = user_name).first()
        if not this_user:
            return render_template("login.html", message = "User not found")
        else:
            try:
                if user_name == this_user.username:
                    if pass_word == this_user.password:
                        login_user(this_user)
                        print("Welcome", this_user.name)
                        return redirect("/dashboard")
                    else:
                        return render_template("login.html", message = "Incorrect password")
            except Exception as e:
                print(e)
                db.session.rollback()
            return redirect("/login")

@app.route('/register', methods = ['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template("register.html")
    else:
        name = request.form.get("name")
        user_name = request.form.get("user_name")
        password = request.form.get("pass")
        exists = Users.query.filter_by(username = user_name).first()
        if exists:
            message = "User Exists!"
            return render_template('register.html', message = message)
        else:
            try:
                date = datetime.now()
                newUser = Users()
                newUser.username = user_name
                newUser.password = password
                newUser.name = name
                newUser.date = date
                db.session.add(newUser)
                db.session.flush()
            except Exception as e:
                print(e)
                db.session.rollback()
            else:
                db.session.commit()
        return redirect('/login')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/login')

@app.route('/librarian_login', methods = ['GET', 'POST'])
def librarian_login():
    if request.method == "GET":
        return render_template("librarian_login.html")
    elif request.method == "POST":
        user_name = request.form.get("user_name")
        pass_word = request.form.get("pass")
        print(user_name, pass_word)
        this_user = Users.query.filter_by(username = user_name).first()
        if not this_user:
            print("User not found")
            return redirect("/librarian_login")
        else:
            try:
                if user_name == this_user.username:
                    if pass_word == this_user.password:
                        login_user(this_user)
                        return redirect("/dashboard")
                    else:
                        print("Incorrect Password")
            except Exception as e:
                print(e)
                db.session.rollback()
            return redirect("/librarian_login")

@app.route('/dashboard')
@login_required
def dashboard():
    user_id = current_user.user_id
    admin = isAdmin(current_user)
    if admin:
        requests = Checkouts.query.join(Books, Checkouts.book_id == Books.book_id).add_columns(Checkouts.checkout_id, Checkouts.user_id, Checkouts.date_requested, Checkouts.status, Checkouts.date_requested, Checkouts.book_id, Books.title).filter(Checkouts.status == "Requested").all()
        issued = Checkouts.query.join(Books, Checkouts.book_id == Books.book_id).add_columns(Checkouts.checkout_id, Checkouts.user_id, Checkouts.date_requested, Checkouts.status, Checkouts.date_issued, Checkouts.book_id, Books.title).filter(Checkouts.status == "Issued").all()
        rejected = Checkouts.query.join(Books, Checkouts.book_id == Books.book_id).add_columns(Checkouts.checkout_id, Checkouts.user_id, Checkouts.date_requested, Checkouts.status, Checkouts.date_rejected, Checkouts.book_id,Books.title).filter(Checkouts.status == "Rejected").limit(5).all()
        revoked = Checkouts.query.join(Books, Checkouts.book_id == Books.book_id).add_columns(Checkouts.checkout_id, Checkouts.user_id, Checkouts.date_requested, Checkouts.status, Checkouts.date_revoked, Checkouts.book_id, Books.title).filter(Checkouts.status == "Revoked").limit(5).all()
        returned = Checkouts.query.join(Books, Checkouts.book_id == Books.book_id).add_columns(Checkouts.checkout_id, Checkouts.user_id, Checkouts.date_requested, Checkouts.status, Checkouts.date_returned, Checkouts.book_id, Books.title).filter(Checkouts.status == "Returned").order_by(Checkouts.date_returned.desc()).limit(5).all()
        return render_template('librarian_dash.html', requests = requests, issued = issued, rejected = rejected, revoked = revoked, returned = returned, admin = True)
    else:
        requests = Checkouts.query.join(Books, Checkouts.book_id == Books.book_id).add_columns(Checkouts.checkout_id, Checkouts.user_id, Checkouts.date_requested, Checkouts.status, Checkouts.date_requested, Checkouts.book_id, Books.title).filter(Checkouts.status == "Requested").filter(Checkouts.user_id == current_user.user_id).all()
        currentbooks = Checkouts.query.join(Books, Checkouts.book_id == Books.book_id).add_columns(Checkouts.checkout_id, Books.book_id, Books.title, Books.author, Books.section_id, Books.isbn_no, Books.description).filter(Checkouts.user_id == user_id).filter(Checkouts.status == "Issued").all()
        returned = Checkouts.query.filter_by(user_id = user_id).filter_by(status = "Returned").all()
        returned_books=[]
        for book in returned:
            bk = Books.query.filter_by(book_id = book.book_id).first()
            bk = Books.query.join(Checkouts, Books.book_id == Checkouts.book_id).add_columns(Checkouts.checkout_id, Books.book_id, Books.title, Books.author, Books.section_id, Books.isbn_no, Books.description).filter(Books.book_id == book.book_id).first()
            returned_books.append(bk)
        purchased = Checkouts.query.join(Books, Checkouts.book_id == Books.book_id).add_columns(Checkouts.checkout_id, Books.book_id, Books.title, Books.author, Books.section_id, Books.isbn_no, Books.description).filter(Checkouts.user_id == user_id).filter(Checkouts.status == "Purchased").distinct().all()
        completed = Checkouts.query.join(Books, Checkouts.book_id == Books.book_id).add_columns(Checkouts.checkout_id, Books.book_id, Books.title, Books.author, Books.section_id, Books.isbn_no, Books.description).filter(Checkouts.user_id == user_id).filter(Checkouts.status == "Returned").distinct().all()
        return render_template('user_dash.html', current_books = currentbooks, returned_books = completed, admin = False, requests = requests, purchased_books = purchased)

@app.route('/latest_books')
@login_required
def latest_books():
    admin = isAdmin(current_user)
    books = Books.query.order_by(Books.datecreated.desc()).all()
    return render_template('latest_books.html', books = books, admin = admin, username = current_user.name)

@app.route('/stats')
@login_required
def stats():
    admin = isAdmin(current_user)
    create_stats(current_user)
    if admin:
        return render_template('stats.html', admin = True)
    else:
        return render_template('stats.html', admin = False)

@app.route('/request/<int:book_id>')
@login_required
def request_book(book_id):
    admin = isAdmin(current_user)
    requested = Checkouts.query.filter_by(user_id = current_user.user_id).filter_by(status = "Requested").all()
    issued = Checkouts.query.filter_by(user_id = current_user.user_id).filter_by(status = "Issued").all()
    i=0
    for book in requested:
        i+=1
    for book in issued:
        i+=1
    if i > 4:
        print("Maximum limit reached")
        message = "Maximum limit reached"
        return redirect(url_for('latest_books', message = message, **request.args))
    else:
        try:
            exists = Checkouts.query.filter_by(user_id = current_user.user_id).filter_by(status = "Requested").filter_by(book_id = book_id).first()
            if exists:
                print("Already requested")
            else:
                checkout = Checkouts()
                checkout.book_id = book_id
                checkout.user_id = current_user.user_id
                date = datetime.now()
                checkout.date_requested = date
                checkout.status = "Requested"
                db.session.add(checkout)
                db.session.flush()
        except Exception as e:
            print(e)
            db.session.rollback()
        finally:
            db.session.commit()
    return redirect('/dashboard')

@app.route('/review/<int:book_id>', methods = ['GET', 'POST'])
@login_required
def review_book(book_id):
    if request.method == 'GET':
        admin = isAdmin(current_user)
        reviewed = Reviews.query.filter_by(user_id = current_user.user_id).filter_by(book_id = book_id).first()
        borrowed = Checkouts.query.filter_by(user_id = current_user.user_id).filter_by(status = "Returned").filter_by(book_id = book_id).all()
        book = Books.query.filter_by(book_id = book_id).first()
        if reviewed:
            print("Book already reviewed")
            return redirect('/dashboard')
        elif not borrowed:
            print("Book not borrowed, so can't give review")
            return redirect('/dashboard')
        return render_template("review.html", reviewed = reviewed, borrowed = borrowed, title = book.title)
    else:
        admin = isAdmin(current_user)
        rating = request.form.get("rating")
        review_text = request.form.get("review_text")
        reviewed = Reviews.query.filter_by(user_id = current_user.user_id).filter_by(book_id = book_id).first()
        borrowed = Checkouts.query.filter_by(user_id = current_user.user_id).filter_by(status = "Returned").filter_by(book_id = book_id).all()
        try:
            review = Reviews()
            review.book_id = book_id
            review.user_id = current_user.user_id
            review.rating = rating
            review.review = review_text
            date = datetime.now()
            review.date_reviewed = date
            book = Books.query.filter_by(book_id = book_id).first()
            reviewed_books = Reviews.query.filter_by(book_id = book_id).all()
            count = 0
            for reviewed_book in reviewed_books:
                rating += reviewed_book.rating
                count += 1
            if count != 0:
                rating = int(int(rating)/int(count))
            book.rating = rating
            db.session.add(review)
            db.session.flush()
        except Exception as e:
            print(e)
            db.session.rollback()
        finally:
            db.session.commit()
        return redirect('/dashboard')

@app.route('/sections')
@login_required
def sections():
    admin = isAdmin(current_user)
    sections = Sections.query.filter_by().all()
    return render_template('sections.html', sections = sections, admin = admin)

@app.route('/<int:section_id>/books')
@login_required
def section_books(section_id):
    admin = isAdmin(current_user)
    books = Books.query.filter_by(section_id = section_id).all()
    section = Sections.query.filter_by(section_id = section_id).first()
    name = section.name
    return render_template('sectionbooks.html', books = books, section_id = section_id, section_name = name, admin = admin)

@app.route('/<int:section_id>/view/books')
@login_required
def view_section_books(section_id):
    admin = isAdmin(current_user)
    books = Books.query.filter_by(section_id = section_id).all()
    section = Sections.query.filter_by(section_id = section_id).first()
    name = section.name
    return render_template('sectionbooks.html', books = books, section_id = section_id, section_name = name, admin = admin)

@app.route('/view/<int:book_id>')
@login_required
def view_book(book_id):
    admin = isAdmin(current_user)
    book = Books.query.filter_by(book_id = book_id).first()
    reviews = Reviews.query.filter_by(book_id = book_id).all()
    if not admin:
        purchased = Checkouts.query.filter_by(book_id = book_id).filter_by(user_id = current_user.user_id).filter_by(status = "Purchased").first()
        borrowed = Checkouts.query.filter_by(book_id = book_id).filter_by(user_id = current_user.user_id).filter_by(status = "Issued").first()
        return render_template('view_book.html', book = book, reviews = reviews, borrowed = borrowed, purchased = purchased, admin = admin)
    else:
        info = Checkouts.query.join(Users, Checkouts.user_id == Users.user_id).add_columns(Checkouts.checkout_id, Checkouts.user_id, Checkouts.date_issued, Checkouts.status, Checkouts.date_requested, Checkouts.book_id, Users.username, Users.name).filter(Checkouts.status == "Issued").order_by(Checkouts.date_issued.asc()).all()
        return render_template('view_book.html', book = book, reviews = reviews, info = info, admin = admin)

@app.route('/view/user/<int:user_id>')
@login_required
def view_user(user_id):
    admin = isAdmin(current_user)
    user_info = Users.query.get(user_id)
    print(user_info)
    books = Checkouts.query.join(Books, Checkouts.book_id == Books.book_id).add_columns(Checkouts.user_id, Checkouts.date_requested, Checkouts.status, Checkouts.date_requested, Checkouts.book_id, Books.title).filter(Checkouts.user_id == user_id).order_by(Checkouts.date_requested.desc()).all()
    reviews = Reviews.query.filter_by(user_id = user_id).all()
    return render_template('view_user.html', books = books, admin = admin, user_id = user_id, user_name = user_info.name, reviews = reviews)

@app.route('/user_dash')
@login_required
def user_dash():
    admin = isAdmin(current_user)
    current = Checkouts.query.filter_by(user_id = current_user.user_id).filter_by(status = "Issued").all()
    current_books=[]
    for book in current:
        bk = Books.query.filter_by(book_id = book.book_id).first()
        bk = Books.query.join(Checkouts, Books.book_id == Checkouts.book_id).add_columns(Checkouts.checkout_id, Books.book_id, Books.title, Books.author, Books.section_id, Books.isbn_no, Books.description).filter(Books.book_id == book.book_id).first()
        print(bk.checkout_id)
        current_books.append(bk)
    returned = Checkouts.query.filter_by(user_id = current_user.user_id).filter_by(status = "Returned").all()
    returned_books=[]
    for book in returned:
        bk = Books.query.filter_by(book_id = book.book_id).first()
        bk = Books.query.join(Checkouts, Books.book_id == Checkouts.book_id).add_columns(Checkouts.checkout_id, Books.book_id, Books.title, Books.author, Books.section_id, Books.isbn_no, Books.description).filter(Books.book_id == book.book_id).first()
        returned_books.append(bk)
    return render_template('user_dash.html', current_books = current_books, returned_books = returned_books)

@app.route('/issue/<int:checkout_id>', methods = ['GET', 'POST'])
@login_required
def issue_book(checkout_id):
    if request.method == "GET":
        book_to_be_issued = Checkouts.query.join(Books, Checkouts.book_id == Books.book_id).add_columns(Checkouts.checkout_id, Checkouts.user_id, Checkouts.date_requested, Checkouts.status, Checkouts.date_requested, Checkouts.book_id, Books.title).filter(Checkouts.checkout_id == checkout_id).first()
        user = Users.query.get(book_to_be_issued.user_id)
        return render_template("issue.html", checkout = book_to_be_issued, user = user, issueDays = issueDays)
    else:
        numOfDays = request.form.get("numberOfDays")
        print(numOfDays)
        checkout = Checkouts.query.filter_by(checkout_id = checkout_id).first()
        book = Books.query.filter_by(book_id = checkout.book_id).first()
        if book.availablecopies <= 0:
            print("Books out of stock")
        else:
            try:
                book.availablecopies -= 1
                date = datetime.now()
                checkout.date_issued = date
                checkout.status = "Issued"
                temp = numOfDays.split()
                if (temp[1] == "second" or temp[1] == "seconds"):
                    checkout.date_to_be_returned = checkout.date_issued + timedelta(seconds = issueDays[numOfDays])
                elif (temp[1] == "minute" or temp[1] == "minutes"):
                    checkout.date_to_be_returned = checkout.date_issued + timedelta(minutes = issueDays[numOfDays])
                elif (temp[1] == "day" or temp[1] == "days"):
                    checkout.date_to_be_returned = checkout.date_issued + timedelta(days = issueDays[numOfDays])
                elif (temp[1] == "week" or temp[1] == "weeks"):
                    checkout.date_to_be_returned = checkout.date_issued + timedelta(weeks = issueDays[numOfDays])
                db.session.flush()
            except Exception as e:
                print(e)
                db.session.rollback()
            finally:
                db.session.commit()
        return redirect('/dashboard')

@app.route('/purchase/<int:book_id>', methods = ['GET', 'POST'])
@login_required
def buy_book(book_id):
    if request.method == "GET":
        book = Books.query.get(book_id)
        return render_template("payment.html", user = current_user, book = book)
    else:
        book = Books.query.filter_by(book_id = book_id).first()
        if book.availablecopies <= 0:
            print("Books out of stock")
        else:
            try:
                checkout = Checkouts()
                checkout.book_id = book_id
                checkout.user_id = current_user.user_id
                date = datetime.now()
                checkout.date_requested = date
                checkout.date_purchased = date
                checkout.status = "Purchased"
                db.session.add(checkout)
                book.availablecopies -= 1
                book.copies -= 1
                db.session.flush()
            except Exception as e:
                print(e)
                db.session.rollback()
            finally:
                db.session.commit()
        return redirect('/dashboard')

@app.route('/download/<int:book_id>')
@login_required
def download_book(book_id):
    admin = isAdmin(current_user)
    borrowed = Checkouts.query.filter_by(book_id = book_id).filter_by(user_id = current_user.user_id).filter_by(status = "Issued").first()
    purchased = Checkouts.query.filter_by(book_id = book_id).filter_by(user_id = current_user.user_id).filter_by(status = "Purchased").first()
    book = Books.query.get(book_id)
    if purchased or admin or borrowed:
        return send_file(f"./data/{book.filename}",mimetype='application/pdf')
    else:
        abort(401)

@app.route('/reject/<int:checkout_id>')
@login_required
def reject_book(checkout_id):
    checkout = Checkouts.query.filter_by(checkout_id = checkout_id).first()
    try:
        date = datetime.now()
        checkout.date_rejected = date
        checkout.status = "Rejected"
    except:
        db.session.rollback()
    finally:
        db.session.commit()
    return redirect('/dashboard')

@app.route('/revoke/<int:checkout_id>')
@login_required
def revoke_book(checkout_id):
    checkout = Checkouts.query.get(checkout_id)
    book = Books.query.get(checkout.book_id)
    try:
        date = datetime.now()
        checkout.date_revoked = date
        checkout.status = "Revoked"
        book.availablecopies += 1
    except Exception as e:
        print(e)
        db.session.rollback()
    finally:
        db.session.commit()
    return redirect('/dashboard')

@app.route('/return/<int:checkout_id>')
@login_required
def return_book(checkout_id):
    checkout = Checkouts.query.get(checkout_id)
    print(checkout)
    book = Books.query.filter_by(book_id = checkout.book_id).first()
    print(book)
    try:
        date = datetime.now()
        checkout.date_returned = date
        book.availablecopies +=1
        checkout.status = "Returned"
        print("Check")
        db.session.flush()
        print("Check")
    except Exception as e:
        print("Check exception")
        print(e)
        db.session.rollback()
    finally:
        db.session.commit()
    return redirect('/dashboard')

@app.route('/section/<int:section_id>/delete')
@login_required
def deletesection(section_id):
    if request.method == "GET":
        try:
            sec = Sections.query.filter_by(section_id = section_id).first()
            books = Books.query.filter_by(section_id = section_id).all()
            for book in books:
                checkouts = Checkouts.query.filter_by(book_id = book.book_id).all()
                reviews = Reviews.query.filter_by(book_id = book.book_id).all()
                for checkout in checkouts:
                    db.session.delete(checkout)
                for review in reviews:
                    db.session.delete(review)
                db.session.delete(book)
            db.session.delete(sec)
            db.session.flush()
        except Exception as e:
            print(e)
            db.session.rollback()
        finally:
            db.session.commit()
        return redirect("/sections")
    
@app.route('/book/<int:book_id>/delete')
@login_required
def deletebook(book_id):
    if request.method == "GET":
        try:
            book = Books.query.filter_by(book_id = book_id).first()
            checkouts = Checkouts.query.filter_by(book_id = book_id).all()
            reviews = Reviews.query.filter_by(book_id = book_id).all()
            for checkout in checkouts:
                db.session.delete(checkout)
            for review in reviews:
                db.session.delete(review)
            db.session.delete(book)
            db.session.flush()
        except Exception as e:
            print(e)
            db.session.rollback()
        finally:
            db.session.commit()
    return redirect("/sections")

@app.route('/add_section', methods = ['GET', 'POST'])
@login_required
def add_section():
    admin = isAdmin(current_user)
    if admin:
        if request.method == 'GET':
            return render_template("add_section.html", admin = True)
        elif request.method == 'POST':
            section_name = request.form.get("section_name")
            description = request.form.get("description")
            exists = Sections.query.filter_by(name = section_name).first()
            try:
                section = Sections()
                section.name = section_name
                date = datetime.now()
                section.date = date
                section.description = description
                db.session.add(section)
                db.session.flush()
            except Exception as e:
                print(e)
                db.session.rollback()
            finally:
                db.session.commit()
            return redirect("/sections")
    else:
        abort(401)

@app.route('/edit_section/<int:section_id>', methods = ['GET', 'POST'])
@login_required
def edit_section(section_id):
    admin = isAdmin(current_user)
    if admin:
        if request.method == 'GET':
            section = Sections.query.filter_by(section_id = section_id).first()
            return render_template("edit_section.html", section = section, admin = True)
        elif request.method == 'POST':
            section = Sections.query.filter_by(section_id = section_id).first()
            section_name = request.form.get("section_name")
            description = request.form.get("description")
            try:
                section.name = section_name
                date = datetime.now()
                section.date = date
                section.description = description
                db.session.flush()
            except Exception as e:
                db.session.rollback()
                print(e)
            finally:
                db.session.commit()
            return redirect("/sections")
    else:
        abort(401)

@app.route("/add_book/<int:section_id>", methods = ['GET', 'POST'])
@login_required
def add_book(section_id):
    admin = isAdmin(current_user)
    if admin:
        if request.method == 'GET':
            sec = Sections.query.filter_by(section_id = section_id).first()
            return render_template("add_book.html", section_id = sec.section_id, admin = True)
        elif request.method == 'POST':
            title = request.form.get("title")
            author = request.form.get("author")
            isbn_no = request.form.get("isbn_no")
            lang = request.form.get("lang")
            pages = request.form.get("pages")
            copies = request.form.get("copies")
            price = request.form.get("price")
            description = request.form.get("description")        
            exists = Books.query.filter_by(isbn_no = isbn_no).first()
            if exists:
                return render_template("alreadyexists.html")
            else:
                try:
                    file = request.files['file']
                    book = Books()
                    book.title = title
                    book.author = author
                    book.isbn_no = int(isbn_no)
                    book.lang = lang
                    book.pages = int(pages)
                    book.description = description
                    book.rating = 0
                    book.copies = int(copies)
                    book.availablecopies = int(copies)
                    date = datetime.now()
                    book.datecreated = date
                    book.section_id = section_id
                    book.filename = file.filename
                    book.price = price
                    filelocation = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
                    file.save(filelocation)
                    db.session.add(book)
                    db.session.flush()
                except Exception as e:
                    print(e)
                    db.session.rollback()
                finally:
                    db.session.commit()
            return redirect("/"+str(section_id)+"/books")
    else:
        abort(401)

@app.route("/edit_book/<int:book_id>", methods = ['GET', 'POST'])
@login_required
def edit_book(book_id):
    admin = isAdmin(current_user)
    if admin:
        if request.method == 'GET':
            book = Books.query.filter_by(book_id = book_id).first()
            sections = Sections.query.filter_by().all()
            return render_template("edit_book.html", book = book, sections = sections, admin = True)
        elif request.method == 'POST':
            borrowed = Checkouts.query.filter(Checkouts.book_id == book_id).filter(Checkouts.status == "Issued").all()
            borrowed_books = 0
            for book in borrowed:
                borrowed_books+=1
            title = request.form.get("title")
            author = request.form.get("author")
            isbn_no = request.form.get("isbn_no")
            lang = request.form.get("lang")
            pages = request.form.get("pages")
            copies = request.form.get("copies")
            price = request.form.get("price")
            section = request.form.get("section")
            description = request.form.get("description")
            book = Books.query.filter_by(book_id = book_id).first()
            try:
                book.title = title
                book.author = author
                book.isbn_no = int(isbn_no)
                book.lang = lang
                book.pages = int(pages)
                book.description = description
                book.rating = 0
                book.copies = int(copies)
                book.availablecopies = book.copies - borrowed_books
                date = datetime.now()
                book.datecreated = date
                book.price = price
                file = request.files['file']
                if file:
                    book.filename = file.filename
                    filelocation = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
                    file.save(filelocation)
                sec = Sections.query.filter_by(name = section).first()
                if sec:
                    book.section_id = sec.section_id
                db.session.flush()
            except Exception as e:
                print(e)
                db.session.rollback()
            finally:
                db.session.commit()
            return redirect("/sections")
    else:
        abort(401)

@app.route('/search')
@login_required
def search():
    admin = isAdmin(current_user)
    searchQuery = request.args.get('searchQuery')
    search = "%{}%".format(searchQuery)
    sections = Sections.query.filter(Sections.name.ilike(search)).all()
    books = Books.query.filter(Books.title.ilike(search)).all()
    isbn = Books.query.filter(Books.isbn_no.ilike(search)).all()
    authors = Books.query.filter(Books.author.ilike(search)).all()
    users = Users.query.filter(Users.username.ilike(search)).all()
    print(sections, books, users)
    books += isbn
    return render_template("search.html", sections = sections, books = books, authors = authors, users = users, admin = admin)

@app.route('/profile', methods = ['GET', 'POST'])
@login_required
def profile():
    admin = isAdmin(current_user)
    user = current_user
    if request.method == "GET":
        return render_template("profile.html", user = user, admin = admin)
    else:
        name = request.form.get("name")
        old_password = request.form.get("old_password")
        new_password = request.form.get("new_password")
        confirm_new_password = request.form.get("confirm_new_password")
        if old_password == user.password:
            if new_password == confirm_new_password:
                try:
                    if name != "":
                        user.name = name
                    if new_password != "":
                        user.password = new_password
                    db.session.flush()
                except Exception as e:
                    print(e)
                    db.session.rollback()
                finally:
                    db.session.commit()
            else:
                return render_template("profile.html", user = user, admin = admin, message = "Passwords don't match")
        else:
            return render_template("profile.html", user = user, admin = admin, message = "Incorrect password")
        return redirect('/dashboard')


@app.errorhandler(401)
def http_error_handler(e):
    return render_template('error.html',code = 401, message = "You are not authorized to access this page"), 401

@app.errorhandler(404)
def not_found(e):
    return render_template('error.html',code = 404, message = "Sorry the page you requested isn't available"), 404

@app.errorhandler(500)
def http_error_handler(e):
    return render_template('error.html',code = 500, message = "Sorry, we encountered an internal server error"), 500
