from flask import request
from flask_restful import Resource, reqparse

from sqlalchemy.exc import DataError
from werkzeug.exceptions import HTTPException

from config import SECRET_KEY
from exceptions.authorization_exception import AuthorizationException
from exceptions.card_exception import CardException
from exceptions.not_found_exception import NotFoundException
from models.card import Card
from models.user import User

from itsdangerous import URLSafeTimedSerializer


class MarketResource(Resource):
    def __init__(self, session, authorization_helper, predict_price):
        self.__session = session
        self.__authorization_helper = authorization_helper
        self.__budget = 500
        self.secret_key = SECRET_KEY
        self.serializer = URLSafeTimedSerializer(self.secret_key)
        self.predict_price = predict_price

    def post(self):
        try:
            authorized_user = self.__authorization_helper.authorization()

            # get request parameters
            post_data = self.get_args(True)

            with self.__session as session:
                # validation
                self.card_validation(post_data['card_id'])
                self.market_price_validation(post_data['market_price'])

                # place card on market
                card = self.__session.query(Card).filter_by(id=post_data['card_id'], user_id=authorized_user.id).first()
                if card:
                    card.market_price = post_data['market_price']
                    card.on_market = True
                    session.commit()
                    return {
                        'message': 'Card placed to the market successfully',
                        'card_id': card.id,
                        'market_price': card.market_price
                    }, 201
                else:
                    return {
                        'message': 'Card was not found',
                        'card_id': post_data['card_id'],
                        'user_id': authorized_user.id
                    }
            # catch req parse exception
        except HTTPException as e:
            if hasattr(e, 'data'):
                return {'error': e.data.get('message', str(e))}, 400
            else:
                return {'error': str(e)}, 400
        except CardException as e:
            return {'error': str(e)}, 401
        except DataError as e:
            return {'error': str(e)}, 400
        except Exception as e:
            return {'error': str(e)}, 400

    def get(self, card_id=None):
        try:
            authorized_user = self.__authorization_helper.authorization()

            with self.__session as session:
                if card_id:
                    # request validation
                    self.card_validation(card_id)
                    card = session.query(Card).filter(
                        Card.id == card_id,
                        Card.on_market == True
                    ).first()
                    if card:
                        return {
                            'card_id': card.id,
                            'card_name': card.name,
                            'card_age': card.age,
                            'card_skill': card.skill,
                            'market_value': card.market_value,
                            'market_price': card.market_price,
                            'owner_id': card.user_id
                        }, 200
                    else:
                        return {
                            'message': 'There is no card with this card_id on market',
                            'card_id': card_id
                        }, 404
                else:
                    # Get query parameters for pagination
                    page = request.args.get('page', default=1, type=int)
                    per_page = request.args.get('per_page', default=2, type=int)

                    # Calculate the offset based on the page and per_page values
                    offset = (page - 1) * per_page

                    # Perform pagination using limit and offset
                    cards = self.__session.query(Card).filter(
                        Card.on_market == True
                    ).limit(per_page).offset(offset).all()
                    if cards:
                        card_data = [
                            {
                                'card_id': card.id,
                                'card_name': card.name,
                                'card_age': card.age,
                                'card_skill': card.skill,
                                'market_value': card.market_value,
                                'market_price': card.market_price,
                                'owner_id': card.user_id
                            }
                            for card in cards
                        ]
                        return card_data, 200
                    else:
                        return {
                            'message': 'There is no cards on market'
                        }, 404
        except AuthorizationException as e:
            return {'error': str(e)}, 401
        except PermissionError as e:
            return {'error': str(e)}, 403
        except DataError as e:
            return {'error': str(e)}, 400
        except Exception as e:
            return {'error': str(e)}, 400

    def patch(self, card_id):
        print(card_id)
        try:
            authorized_user = self.__authorization_helper.authorization()

            with self.__session as session:

                if card_id:
                    # request validation
                    self.card_validation(card_id)

                    card = self.__session.query(Card).filter_by(id=card_id, on_market=True).first()
                    if authorized_user.id == card.user_id:
                        card.on_market = False
                        session.commit()
                        return {
                            'message': 'The card has been withdrawn from sale successfully',
                            'card_id': card.id,
                            'owner_id': authorized_user.id
                        }, 201

                    if card and int(authorized_user.budget) >= int(card.market_price):
                        owner = self.__session.query(User).filter_by(id=card.user_id).first()
                        buyer = self.__session.query(User).filter_by(id=authorized_user.id).first()
                        buyer.budget = int(buyer.budget) - int(card.market_price)
                        owner.budget = int(owner.budget) + int(card.market_price)
                        card.user_id = buyer.id
                        card.market_value = int(card.market_price)
                        card.on_market = False
                        session.commit()

                        self.predict_price.predict_and_update_prices()

                        return {
                            'card_id': card.id,
                            'card_name': card.name,
                            'card_age': card.age,
                            'card_skill': card.skill,
                            'market_value': card.market_value,
                            'market_price': card.market_price,
                            'owner_id': owner.id,
                            'buyer_id': buyer.id,
                            'buyer_budget': buyer.budget,
                            'owner_budget': owner.budget,    #for test
                            'card_on_market': card.on_market,           #for test
                            'message': 'Card was bought successfully',
                        }, 201
                    elif not card:
                        return {
                            'message': 'There is no card with this card_id on market',
                            'card_id': card_id
                        }, 404
                    elif authorized_user.budget < card.market_price:
                        return {
                            'message': 'You do not have enough money',
                            'budget': authorized_user.budget,
                            'card_price': card.market_price
                        }, 201
        except NotFoundException as e:
            return {'error': str(e)}, 404
        except AuthorizationException as e:
            return {'error': str(e)}, 401
        except PermissionError as e:
            return {'error': str(e)}, 403
        except Exception as e:
            return {'error': str(e)}, 400

    def check_permission(self, user, user_id):
        # Deny access if not admin and requested another user id
        if not user.role == 'admin' and user.id != user_id:
            raise PermissionError('Forbidden')

    def get_args(self, is_required=False):
        parser = reqparse.RequestParser()
        parser.add_argument('card_id', required=is_required, help='card_id is required')
        parser.add_argument('market_price', required=is_required, help='market_price is required')
        return parser.parse_args()

    @staticmethod
    def is_integer(value):
        try:
            int(value)
            return True
        except ValueError:
            return False

    def card_validation(self, card_id):
        if not self.is_integer(card_id):
            raise Exception('Invalid card_id')

    def market_price_validation(self, market_price):
        if not self.is_integer(market_price):
            raise Exception('Invalid market_price')
