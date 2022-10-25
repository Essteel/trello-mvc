from flask import Blueprint, request, abort
from sqlalchemy.exc import IntegrityError
from flask_jwt_extended import create_access_token, get_jwt_identity

from init import db, bcrypt
from models.user import User, UserSchema
from datetime import timedelta

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/register/', methods = ['POST'])
def auth_register():
    try:
        # Create a new User model instance
        user = User(
            email = request.json['email'],
            password = bcrypt.generate_password_hash(request.json['password']).decode('utf-8'),
            name = request.json.get('name')
        )
        # Add and commit user to the database
        db.session.add(user)
        db.session.commit()
        return UserSchema(exclude=['password']).dump(user), 201
    except IntegrityError:
        return {'error' : 'Email address already in use'}, 409

@auth_bp.route('/login/', methods = ['POST'])
def auth_login():
    # Get user by email address
    # stmt = db.select(User).where(User.email == request.json['email']) # how to do with Where
    stmt = db.select(User).filter_by(email=request.json['email'])
    user = db.session.scalar(stmt)
    # If user is valid check password, if also true return user, no password
    if user and bcrypt.check_password_hash(user.password, request.json['password']):
        # return UserSchema(exclude=['password']).dump(user)
        token = create_access_token(identity=str(user.id), expires_delta=timedelta(days=1))
        return {'email': user.email, 'token' : token, 'is_admin' : user.is_admin}
    else:
        return {'error' : 'Invalid email or password'}, 401

def authorize():
    user_id = get_jwt_identity() # get user from token
    stmt = db.select(User).filter_by(id=user_id) # query to db to get user with that id
    user = db.session.scalar(stmt) # set user
    if not user.is_admin:
        abort(401)
