from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from init import db
from models.card import Card, CardSchema
from models.comment import Comment, CommentSchema
from datetime import date
from controllers.auth_controller import authorize

cards_bp = Blueprint('cards', __name__, url_prefix = '/cards')

@cards_bp.route('/')
def get_all_cards():
    stmt = db.select(Card).order_by(Card.date.desc())
    cards = db.session.scalars(stmt)
    return CardSchema(many=True).dump(cards)

@cards_bp.route('/<int:id>/')
def get_one_card(id):
    stmt = db.select(Card).filter_by(id=id)
    card = db.session.scalar(stmt)
    if card:
        return CardSchema().dump(card)
    else:
        return {'error': f'Card not found with id {id}'}, 404

@cards_bp.route('/<int:id>/', methods=['DELETE'])
@jwt_required()
def delete_one_card(id):
    authorize()
    stmt = db.select(Card).filter_by(id=id)
    card = db.session.scalar(stmt)
    if card:
        db.session.delete(card)
        db.session.commit()
        return {'message': f"Card '{card.title}' deleted successfully"}
    else:
        return {'error': f'Card not found with id {id}'}, 404

@cards_bp.route('/<int:id>/', methods=['PUT', 'PATCH'])
@jwt_required()
def update_one_card(id):
    stmt = db.select(Card).filter_by(id=id)
    card = db.session.scalar(stmt)
    if card:
        # update card attribute to what is set or leave unchanged if no new value given (or statement = 'short circuiting)
        card.title = request.json.get('title') or card.title
        card.description = request.json.get('description') or card.description
        card.status = request.json.get('status') or card.status
        card.priority = request.json.get('priority') or card.priority
        db.session.commit()
        return CardSchema().dump(card)
    else:
        return {'error': f'Card not found with id {id}'}, 404

@cards_bp.route('/', methods = ['POST'])
@jwt_required()
def create_card():
    # Create a new card model instance
    card = Card(
        title = request.json['title'],
        description = request.json['description'],
        date = date.today(),
        status = request.json['status'],
        priority = request.json['priority'],
        user_id = get_jwt_identity()
    )
    # Add and commit card to the database
    db.session.add(card)
    db.session.commit()
    return CardSchema().dump(card), 201

@cards_bp.route('/<int:card_id>/comments/', methods = ['POST'])
@jwt_required()
def create_comment(card_id):
    stmt = db.select(Card).filter_by(id=card_id)
    card = db.session.scalar(stmt)
    if card:
        # Create a new comment model instance
        comment = Comment(
            message = request.json['message'],
            user_id = get_jwt_identity(),
            card_id = card_id,
            date = date.today()
        )
        # Add and commit comment to the database
        db.session.add(comment)
        db.session.commit()
        return CommentSchema().dump(comment), 201
    else:
        return {'error': f'Card not found with id {id}'}
