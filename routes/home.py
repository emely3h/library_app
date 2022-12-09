from flask import flash, redirect, render_template, request, make_response, request, url_for, Blueprint, request
from flask_jwt_extended import current_user, get_csrf_token
from flask_jwt_extended import jwt_required
from models import Book, Rental, Status, BookRequest
from main import db

home_routes = Blueprint('home_routes', __name__, template_folder='templates')



@home_routes.route("/", methods=['GET'])
def home():
    logged_in = False
    try:
        books = db.session.query(Book).filter(Book.status != Status.removed).all()
        jwt = request.cookies.get('access_token_cookie')
        csrf = ''
        csrf = get_csrf_token(jwt)
        logged_in = True
    except Exception as e:
        csrf = 'not-valid'
    response = make_response(render_template("home.html", books=books, logged_in=logged_in, csrf_token=csrf))
    return response



@home_routes.route('/borrow-book', methods=['POST'])
@jwt_required()
def borrow_book():
    id= request.form.get('id')
    book = db.session.query(Book).filter_by(id=id).one_or_404()
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
    return make_response(redirect(url_for('home_routes.home')))

@home_routes.route("/book-request", methods=['GET', 'POST'])
def book_request():
    if request.method == 'POST':
        data = request.form
        title, author, message = data.get('title'), data.get('author'), data.get('message')
        if len(title) > 3 and  len(author) > 3:
            book_request = BookRequest(title=title, author=author, message=message)
            db.session.add(book_request)
            db.session.commit()
            flash('Book request successfully forwarded.', 'success')
            return make_response(redirect(url_for('home_routes.home')))
        else:
            flash('Enter a valid author and title to make a book request.')
    return make_response(render_template("book_request.html"))

@home_routes.route('/request', methods=['POST'])
@jwt_required()
def request_borrowed_book():
    id = request.form.get('id')
    book = db.session.query(Book).filter_by(id=id, status=Status.borrowed).one_or_404()
    rental = db.session.query(Rental).filter(Rental.book_id == book.id, Rental.return_date == None).one_or_404()
    rental.extending = False
    db.session.add(rental)
    db.session.commit()
    flash('Request successfully made.', 'success')
    return make_response(redirect(url_for('home_routes.home')))


@home_routes.route('/reading-list', methods=['POST', 'DELETE'])
@jwt_required()
def reading_list():
    method = request.form.get('method')

    book = db.session.query(Book).filter_by(id=request.form.get('id')).one_or_404()
    
    if method == 'add': #request.method == 'POST':
        if book in current_user.books:
            flash('This book already has been added to your reading list.', 'info')
        else:
            current_user.books.append(book)
            db.session.add(current_user)
            db.session.commit()
            flash('Book successfully added to your reading list.', 'success')
    if method == 'delete': #elif request.method == 'DELETE':
        if book not in current_user.books:
            flash('This book is not in your reading list.', 'info')
        else:
            current_user.books.remove(book)
            db.session.add(current_user)
            db.session.commit()
            flash('Book successfully removed from your reading list.', 'success')
    return make_response(redirect(url_for('home_routes.home')))
