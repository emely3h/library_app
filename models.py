from datetime import datetime, timedelta
from main import db
import enum
from sqlalchemy import Boolean, DateTime, Enum, exc
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash
import logging
import os

class Roles(enum.Enum):
    admin = "admin"
    user = "user"

class Status(enum.Enum):
    available = "available"
    borrowed = "borrowed"
    missing = "missing"
    removed = 'removed'

reading_list = db.Table('reading_list', 
    db.Column('id', db.Integer, primary_key=True),
    db.Column('book_id', db.Integer, db.ForeignKey('book.id')),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
)

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(), nullable=False)
    role = db.Column(Enum(Roles))
    rentals = relationship('Rental')
    #reading_list = relationship('Book')
    books = db.relationship('Book', secondary=reading_list, backref='books')

    def __init__(self, username, email, password, role, **kwargs):
        super(User, self).__init__(**kwargs)
        self.username = username
        self.email = email
        self.password = generate_password_hash(password)
        self.role = role
# Question: which secret key is generate_password hash using?

class Book (db.Model):
    __tablename__ = 'book'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    author = db.Column(db.String(120), nullable=False)
    description = db.Column(db.String(500), nullable=False)
    status = db.Column(Enum(Status))
    rentals = relationship('Rental')
    users = db.relationship('User', secondary=reading_list, backref='users')

class Rental(db.Model): 
    __tablename__ = 'rental'
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey(Book.id))
    user_id = db.Column(db.Integer, db.ForeignKey(User.id))
    borrow_date = db.Column(DateTime, nullable=False)
    due_date = db.Column(DateTime, nullable=False)
    return_date = db.Column(DateTime, nullable=True)
    extending = db.Column(Boolean, nullable=False)
    def __init__(self, book_id, user_id, **kwargs):
        super(Rental, self).__init__(**kwargs)
        self.book_id = book_id
        self.user_id = user_id
        self.borrow_date = datetime.utcnow()
        self.due_date = datetime.utcnow() + timedelta(int(os.getenv('STANDARD_RENTAL_TIME')))
        self.extending = True


class TokenBlocklist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(36), nullable=False, index=True)
    created_at = db.Column(db.DateTime, nullable=False)

class BookRequest (db.Model):
    __tablename__ = 'book_request'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    author = db.Column(db.String(120), nullable=False)
    message = db.Column(db.String(500), nullable=True)

def db_seed():
    if db.session.query(Book).filter_by(id=1) is None:
        admin = User(username = 'admin', email = 'admin@gmail.com', role=Roles.admin, password = os.getenv('ADMIN_PASSWORD'))
        user1 = User(username = 'test', email = 'test@gmail.com', role=Roles.user, password = 'ASDFasdf5%')
        book1 = Book(title = 'Introduction to Software Architecture', author="author xy", description="This is the best book to learn about software architecture", status=Status.available)
        book2 = Book(title = 'Introduction to Clean Code', author="author xy", description="This is the best book to learn about clean code", status=Status.available)
        # rental = Rental(book1.id, user1.id)
        print('TEST 1')
        try:
            db.session.add(admin)
            db.session.add(user1)
            db.session.add(book1)
            db.session.add(book2)
            # db.session.add(rental)
            db.session.commit()
        except exc.SQLAlchemyError as e:
            logging.error(e) 
    else:
        logging.info('DB already has been seeded')
    

