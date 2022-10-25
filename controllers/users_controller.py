from flask import Blueprint, request
from flask_jwt_extended import jwt_required

from init import db, bcrypt
from models.user import User, UserSchema
from controllers.auth_controller import authorize

users_bp = Blueprint('users', __name__, url_prefix = '/users')

@users_bp.route('/')
@jwt_required()
def get_all_users():
    authorize()
    stmt = db.select(User).order_by(User.id.desc())
    users = db.session.scalars(stmt)
    return UserSchema(exclude=['password'], many=True).dump(users)

@users_bp.route('/<int:id>/')
@jwt_required()
def get_one_user(id):
    authorize()
    stmt = db.select(User).filter_by(id=id)
    user = db.session.scalar(stmt)
    if user:
        return UserSchema(exclude=['password']).dump(user)
    else:
        return {'error': f'User not found with id {id}'}, 404

@users_bp.route('/<int:id>/', methods=['DELETE'])
@jwt_required()
def delete_one_user(id):
    authorize()
    stmt = db.select(User).filter_by(id=id)
    user = db.session.scalar(stmt)
    if user:
        db.session.delete(user)
        db.session.commit()
        return {'message': f"User '{user.name}' deleted successfully"}
    else:
        return {'error': f'User not found with id {id}'}, 404

@users_bp.route('/<int:id>/', methods=['PUT', 'PATCH'])
@jwt_required()
def update_one_user(id):
    authorize()
    stmt = db.select(User).filter_by(id=id)
    user = db.session.scalar(stmt)
    if user:
        # update user attribute to what is set or leave unchanged if no new value given (or statement = 'short circuiting)
        user.name = request.json.get('name') or user.name
        user.email = request.json.get('email') or user.email
        user.password = bcrypt.generate_password_hash(request.json.get('password')).decode('utf-8') or user.password
        user.is_admin = request.json.get('is_admin') or user.is_admin
        db.session.commit()
        return UserSchema(exclude=['password']).dump(user)
    else:
        return {'error': f'User not found with id {id}'}, 404
