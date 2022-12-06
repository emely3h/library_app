
from curses import flash
from flask import Blueprint, make_response, redirect, render_template, request, url_for

from models import Book, Status, Rental, User
from main import db


book_routes = Blueprint('book_routes', __name__, template_folder='templates')

# admin should also have the option to return the book or mark the book as missing
@book_routes.route("/book/<id>", methods=['GET'])
def book_details(id):
    id= int(id)
    book = db.session.query(Book).filter_by(id=id).first()
    if book is not None:
        current_owner, due_date = None, None
        if book.status == Status.borrowed:
            rental = db.session.query(Rental).filter_by(book_id = book.id, return_date = None).one_or_404()
            due_date = rental.due_date 
            current_owner = db.session.query(User).filter_by(id=rental.user_id).one_or_404().username
        # missing: renting history for admin users
        return make_response(render_template("book.html", book=book, current_owner=current_owner, due_date=due_date ))
    else:
        flash('The book you are looking for does not exist.', 'error')
    return make_response(redirect(url_for('home')))