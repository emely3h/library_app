from functools import wraps
from flask import Blueprint, flash, make_response, redirect, render_template, request, url_for
from flask_jwt_extended import current_user, get_csrf_token, get_jwt_identity, verify_jwt_in_request
from main import db
from models import Book, Status, User, Roles


admin_routes = Blueprint('admin_routes', __name__, template_folder='templates')


def admin_required():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            if current_user.role == Roles.admin:
                return fn(*args, **kwargs)
            else:
                flash('Admins only!', 'error')
                return make_response(redirect(url_for('home_routes.home')), 403)
        return decorator
    return wrapper

@admin_routes.route("/admin", methods=['GET'])
@admin_required()
def admin_page():
    borrowed_books = db.session.query(Book).filter_by(status=Status.borrowed)
    missing_books = db.session.query(Book).filter_by(status=Status.missing)
    csrf = get_csrf_token(request.cookies.get('access_token_cookie'))
    return make_response(render_template('admin.html', borrowed_books=borrowed_books, missing_books=missing_books, csrf_token=csrf))

@admin_routes.route('/admin/add-book', methods=['POST'])
@admin_required()
def add_book():
    form_data = request.form
    title, author, description = form_data.get('title'), form_data.get('author'), form_data.get('description')
    if len(title) < 5 or len(author) < 5 or len(description) < 15:
        flash('Title and author have a min length of 5, description has a min. length of 15.', 'error')
    else:
        book = Book(title=title, author=author, description=description, status =Status.available)
        try:
            db.session.add(book)
            db.session.commit()
        except:
            flash('Error occdurred')
        flash('Book successfully added.', 'success')
    return make_response(redirect(url_for('admin_routes.admin_page')))

@admin_routes.route('/admin/book-status', methods=['POST'])
@admin_required()
def change_book_status():
    id = request.form.get('id')
    status = get_status(request.form.get('status'))
    book = db.session.query(Book).filter_by(id=id).one_or_404()
    book.status = status
    try:
        db.session.add(book)
        db.session.commit()
    except:
        flash('Error occdurred')
    flash('Book status successfully changed.', 'success')
    return make_response(redirect(url_for('admin_routes.admin_page')))


def get_status(status):
    if status == Status.available.name:
        return Status.available
    else:
        return Status.missing
