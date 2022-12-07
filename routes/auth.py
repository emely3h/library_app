import datetime
from functools import wraps
from flask import Blueprint, flash, redirect, render_template, request, make_response, jsonify, url_for, current_app
from werkzeug.security import check_password_hash
import re
from main import jwt
from main import db
from models import TokenBlocklist, User, Roles
from flask_jwt_extended import create_access_token, get_jwt, get_jwt_identity, jwt_required, set_access_cookies, verify_jwt_in_request
import os

login_routes = Blueprint('login_routes', __name__, template_folder='templates')


@login_routes.route('/auth/login', methods=['POST', 'GET'])
def sign_up():
    if request.method == 'GET':
        return make_response(render_template('login.html'))
    elif request.method == 'POST':
        try:
            data = request.form
            email, password = data.get('email'), data.get('password')

            user = db.session.query(User).filter_by(email=email).first()    

            if user is not None and check_password_hash(user.password, password) == True:
                access_token = create_access_token(identity=user.id)
                response = redirect(url_for('home_routes.home'))
                set_access_cookies(response, access_token)
                flash(f'Successfully logged in. Welcome {user.username}!', 'info')
                return response
                    
            else:
                raise ValueError('Invalid email or password')
        except ValueError as vex:
            return make_response(render_template('login.html', error=str(vex)), 400)

@login_routes.route('/auth/register', methods=['POST', 'GET'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    if request.method == 'POST':
        try:
            data = request.form
            email, password, password_confirm, username = data.get('email'), data.get('password'), data.get('password_confirm'), data.get('username')
            if email == '' or password == '' or username == '' or password_confirm == '':
                raise ValueError("Email, password, password-confirm field and username can not be empty.")
            if check_user_exists(email) is True:
                raise ValueError("User already exists, please log in.")
            if check_email(email) == False:
                raise ValueError('Enter a valid email adress.')
            if check_password(password) == False:
                raise ValueError("Password has to be 7-20 characters long, contain a small and big character, a number and a special character!")
            if password != password_confirm:
                raise ValueError("Password have to match")

            new_user = User(username=username, email=email, password=password, role=Roles.user)
            db.session.add(new_user)
            db.session.commit()

            access_token = create_access_token(identity=new_user.id)
            response = redirect(url_for('home_routes.home'))
            set_access_cookies(response, access_token)

            flash(f'Successfully registered and logged in. Welcome {new_user.username}!', 'info')
            return redirect(url_for('home_routes.home'))
        except ValueError as vex:
            return make_response(render_template('register.html', error=str(vex)), 400)
        except Exception as ex:
            print(ex)
            return make_response(render_template('register.html', error='Some error occurred. Please try again.'), 500)

@jwt.user_identity_loader
def user_identity_lookup(user):
    return user

@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    identity = jwt_data["sub"]
    return User.query.filter_by(id=identity).one_or_none()


@login_routes.route("/auth/logout", methods=['POST'])
@jwt_required()
def modify_token():
    jti = get_jwt()["jti"]
    now = datetime.datetime.now(datetime.timezone.utc)
    db.session.add(TokenBlocklist(jti=jti, created_at=now))
    db.session.commit()
    flash('Successfully logged out.', 'success')
    return make_response(redirect(url_for('home_routes.home')))

@current_app.after_request
def refresh_expiring_jwts(response):
    try:
        exp_timestamp = get_jwt()["exp"]
        now = datetime.datetime.now(datetime.timezone.utc)
        target_timestamp = datetime.datetime.timestamp(now + datetime.timedelta(minutes=3))
        if target_timestamp > exp_timestamp:
            access_token = create_access_token(identity=get_jwt_identity())
            set_access_cookies(response, access_token)
        return response
    except (RuntimeError, KeyError):
        # Case where there is not a valid JWT. Just return the original response
        return response

@jwt.token_in_blocklist_loader
def check_if_token_is_revoked(jwt_header, jwt_payload: dict):
    jti = jwt_payload["jti"]
    jti = jwt_payload["jti"]
    token = db.session.query(TokenBlocklist.id).filter_by(jti=jti).scalar()

    return token is not None


@jwt.unauthorized_loader
def token_invalid():
    flash('Please log in.', 'error')
    return make_response(redirect(url_for('home_routes.home')), 401) # should add status code 401, problem with redirect page showing

@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    flash('Token expired, please log in again.', 'error')
    return make_response(redirect(url_for('home_routes.home')), 401)

@jwt.revoked_token_loader
def token_revoked_callback(jwt_header, jwt_payload):
    flash('You are currently logged out, log in again.', 'error')
    return make_response(redirect(url_for('home_routes.home')), 401)


def check_email(email):  
    if(re.search(os.getenv("EMAIL_REGEX"),email)):  
        return True  
    else:  
        return False 

def check_password(password):
    if len(password) >= 6 and len(password) <= 20 and any(char.isdigit() for char in password) \
        and any(char.isupper() for char in password) and any(char.islower() for char in password):
        return True
    else:
        return False

def check_user_exists(email):
    return db.session.query(User.email).filter_by(email=email).first() is not None



