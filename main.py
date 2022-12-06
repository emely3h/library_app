from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

from flask_jwt_extended import JWTManager
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()
import os


jwt = JWTManager()
db = SQLAlchemy()

def create_app():
    app = Flask(__name__)


    app.secret_key =  os.getenv("SECRET_KEY")
    app.config["TEMPLATES_AUTO_RELOAD"] = True

    app.config["JWT_COOKIE_SECURE"] = False

    app.config["JWT_SECRET_KEY"] = os.getenv("SECRET_KEY")

    app.config['JWT_TOKEN_LOCATION'] = ['cookies']
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(minutes=10)

    app.config['JWT_COOKIE_CSRF_PROTECT'] = True 
    app.config['JWT_CSRF_CHECK_FORM'] = True
    app.config['JWT_ACCESS_CSRF_FIELD_NAME'] = 'csrf_token'


    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///project.db"

    db.init_app(app)
    jwt.init_app(app)

    from models import db_seed
    
    if __name__ == 'main':
        app.run(debug=True) 

    with app.app_context():
        
        db.create_all()
        db_seed()

        from routes.auth import login_routes
        from routes.admin import admin_routes
        from routes.book import book_routes
        from routes.my_books import my_books_routes
        from routes.home import home_routes

        app.register_blueprint(admin_routes)
        app.register_blueprint(login_routes)
        app.register_blueprint(book_routes)
        app.register_blueprint(my_books_routes)
        app.register_blueprint(home_routes)
        return app





