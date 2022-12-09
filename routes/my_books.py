from flask import Blueprint, make_response, redirect, render_template, request, url_for, flash
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
        if rental.return_date is None:
            rental_books.append((rental,db.session.query(Book).filter_by(id=rental.book_id).first()))
    response = make_response(render_template("my_books.html", rental_books=rental_books, csrf_token=csrf, reading_list=current_user.books, test = "javascript:alert('unsafe');"))
    
    return response


@my_books_routes.route('/my-books/extend', methods=['POST'])
@jwt_required()
def extend_book():
    id = int(request.form.get('id'))

    rental = db.session.query(Rental).filter_by(book_id=id, user_id=current_user.id).one_or_404()
    
    if rental.extending is True:
        rental.extending = False
        rental.due_date = rental.due_date + timedelta(days=int(os.getenv('EXTENSION_TIME')))
        db.session.add(rental)
        db.session.commit()
        flash('Lending period successfully extended.', 'success')
    else:
        flash('Extending not possible, you either already extended or someone else is requesting the book.', 'error')
    return make_response(redirect(url_for('my_books_routes.my_books_page')))
            