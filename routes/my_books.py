from curses import flash
from flask import Blueprint, make_response, redirect, render_template, request, url_for
from flask_jwt_extended import current_user, get_csrf_token, jwt_required

from models import Rental, Book
from main import db
from datetime import timedelta
import os



my_books_routes = Blueprint('my_books_routes', __name__, template_folder='templates')

@my_books_routes.route("/my-books", methods=['GET'])
@jwt_required()
def my_books_page():    
    rental_books = []
    csrf = get_csrf_token(request.cookies.get('access_token_cookie'))
    for rental in current_user.rentals:
        rental_books.append((rental,db.session.query(Book).filter_by(id=rental.book_id).first()))

    return make_response(render_template("my_books.html", rental_books=rental_books, csrf_token=csrf, reading_list=current_user.books))


@my_books_routes.route('/my-books/extend', methods=['POST'])
@jwt_required()
def extend_book():
    print('ENTERED 123')
    id = int(request.form.get('id'))

    rental = db.session.query(Rental).filter_by(book_id=id, user_id=current_user.id).one_or_404()

    if rental is None:
        flash('you can only renew books that you are currently borrowing.', 'error')
    else:
        if rental.extended is False:
            rental.extended = True
            rental.due_date = rental.due_date + timedelta(days=os.getenv('EXTENSION_TIME'))
            db.session.add(rental)
            db.session.commit()
            flash('Lending period successfully extended', 'success')
        else:
            flash('You can only extend the renting period once.', 'error')
        flash('Some error occured, please try again.', 'error')
    return make_response(redirect(url_for('my_books_routes.my_books_page')))
            