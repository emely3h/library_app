from flask import flash, redirect, render_template, request, make_response, request, url_for, current_app, Blueprint
from flask_jwt_extended import current_user, get_csrf_token, verify_jwt_in_request
from flask_jwt_extended import jwt_required
from models import Book, Rental, Status
from main import db

import logging

home_routes = Blueprint('home_routes', __name__, template_folder='templates')



@home_routes.route("/", methods=['GET'])
def home():
    logged_in = False
    try:
        books = Book.query.all()
        """ value = "javascript:alert('unsafe')" """
        jwt = request.cookies.get('access_token_cookie')
        csrf = ''
        csrf = get_csrf_token(jwt)
        logged_in = True
    except Exception as e:
        print('e entered !!!')
        csrf = 'not-valid'
    response = make_response(render_template("home.html", books=books, logged_in=logged_in, csrf_token=csrf))
    
    # response.headers['Content-Security-Policy'] = "style-src https://cdn.jsdelivr.net/npm/bootstrap@4.3.1/dist/css/bootstrap.min.css" include also main.css
    return response



@home_routes.route('/borrow-book', methods=['POST'])
@jwt_required()
def borrow_book():
    id= int(request.form.get('id'))# what happens if id NONE?
    book = db.session.query(Book).filter_by(id=id).first()
    if book is not None:
        if book.status == Status.available:
            book.status = Status.borrowed
            rental = Rental(book.id, current_user.id)
            db.session.add(current_user)
            db.session.add(book)
            db.session.add(rental)
            db.session.commit()
            flash('Book successfully borrowed!', 'success')
        else:
            flash(f'Book is currently {book.status.name}!', 'error')
    else:
        flash('The book you are looking for does not exist.', 'error')
        return make_response(redirect(url_for('home')))
    return make_response(redirect(url_for('home')))

@home_routes.route("/book-request", methods=['GET'])
def book_request():
    return make_response(render_template("book_request.html"))

@home_routes.route('/reading-list', methods=['POST', 'DELETE'])
def reading_list():

    jwt = verify_jwt_in_request(optional=True)
    if jwt is None:
        flash('You need to login first.', 'error')
    else:
        book = db.session.query(Book).filter_by(id=request.form.get('id')).one_or_404()
        
        if request.method == 'POST':
            if book in current_user.books:
                flash('This book has already been added to your reading list.', 'info')
            else:
                current_user.books.append(book)
                db.session.add(current_user)
                db.session.commit()
                flash('Book successfully added to your reading list.', 'success')
        elif request.method == 'DELETE':
            print('entered')
            if book not in current_user.books:
                flash('This book is not in your reading list.', 'info')
            else:
                current_user.books.remove(book)
                flash('Book successfully removed from your reading list.', 'success')
    return make_response(redirect(url_for('home')))


@current_app.errorhandler(404)
def page_not_found(e):
    logging.error(e)
    return render_template("404.html"), 404

@current_app.errorhandler(500)
def internal_server_error(e):
    logging.error(e)
    return render_template("500.html"), 500

