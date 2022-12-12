
from curses import flash
from flask import Blueprint, make_response, redirect, render_template, request, url_for
from flask_jwt_extended import verify_jwt_in_request, current_user
from models import Book, Status, Rental, User, Roles
from main import db


book_routes = Blueprint('book_routes', __name__, template_folder='templates')

@book_routes.route("/book", methods=['GET'])
def book_details():

    id= int(request.args.get('id'))
    book = db.session.query(Book).filter_by(id=id).one_or_404()
    if book is not None:
        current_owner, due_date, renting_hisotry, admin = None, None, None, None
        if book.status == Status.borrowed:
            rental = db.session.query(Rental).filter_by(book_id = book.id, return_date = None).one()
            due_date = rental.due_date 
            current_owner = db.session.query(User).filter_by(id=rental.user_id).one().username
        
        jwt = verify_jwt_in_request(optional=True)  # bug: if jwt was revoked throws exception
        
        if current_user is not None and current_user.role == Roles.admin:
            admin = True
            renting_hisotry = db.session.query(Rental).filter_by(book_id=book.id).order_by(Rental.borrow_date.desc())
            renting_hisotry = renting_hisotry[:10]
            users = []
            for rental in renting_hisotry:
                user = db.session.query(User).filter_by(id=rental.user_id).first()
                users.append(user.username)
                print(user.username)

        return make_response(render_template("book.html", book=book, current_owner=current_owner, due_date=due_date, renting_hisotry=renting_hisotry, users=users, admin=admin ))
    else:
        flash('The book you are looking for does not exist.', 'error')
    return make_response(redirect(url_for('home_routes.home')))