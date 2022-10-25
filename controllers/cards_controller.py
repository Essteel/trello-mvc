from flask import Blueprint, request

from db import db
from models.card import Card, CardSchema
from datetime import date

cards_bp = Blueprint('cards', __name__, url_prefix = '/cards')

@cards_bp.route('/')
# @jwt_required()
def get_all_cards():
    # user_id = get_jwt_identity() # get user from token
    # stmt = db.select(User).filter_by(id=user_id) # query to db to get user with that id
    # user = db.session.scalar(stmt) # set user
    # if not authorize():
    #     return {'error' : 'You must be an admin'}, 401
    # select * from cards
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

@cards_bp.route('/<int:id>/', methods=['PUT', 'PATCH'])
def update_one_card(id):
    stmt = db.select(Card).filter_by(id=id)
    card = db.session.scalar(stmt)
    if card:
        card.title = request.json['title'] or card.title
        card.description = request.json['description'] or card.description
        card.status = request.json['status'] or card.status
        card.priority = request.json['priority'] or card.priority
        db.session.commit()
        return CardSchema().dump(card)
    else:
        return {'error': f'Card not found with id {id}'}, 404

@cards_bp.route('/', methods = ['POST'])
def create_card():
    # Create a new card model instance
    card = Card(
        title = request.json['title'],
        description = request.json['description'],
        date = date.today(),
        status = request.json['status'],
        priority = request.json['priority']
    )
    # Add and commit card to the database
    db.session.add(card)
    db.session.commit()
    return CardSchema().dump(card), 201
