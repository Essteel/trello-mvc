from flask import Blueprint

from db import db
from models.card import Card, CardSchema

cards_bp = Blueprint('cards', __name__, url_prefix = '/cards')

@cards_bp.route('/')
# @jwt_required()
def all_cards():
    # user_id = get_jwt_identity() # get user from token
    # stmt = db.select(User).filter_by(id=user_id) # query to db to get user with that id
    # user = db.session.scalar(stmt) # set user
    # if not authorize():
    #     return {'error' : 'You must be an admin'}, 401
    # select * from cards
    stmt = db.select(Card).order_by(Card.priority.desc(), Card.title)
    cards = db.session.scalars(stmt)
    return CardSchema(many=True).dump(cards)
