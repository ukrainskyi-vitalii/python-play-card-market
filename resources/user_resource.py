import asyncio
import json
import aiohttp
import random
import bcrypt

from flask import request
from flask_restful import Resource, reqparse

from sqlalchemy.exc import DataError
from werkzeug.exceptions import HTTPException

from config import SECRET_KEY, FOOTBALL_API_LEAGUE_ID, FOOTBALL_API_KEY
from exceptions.authorization_exception import AuthorizationException
from exceptions.card_exception import CardException
from exceptions.not_found_exception import NotFoundException
from models.card import Card
from models.user import User
from email_validator import validate_email, EmailNotValidError

from itsdangerous import URLSafeTimedSerializer


class UserResource(Resource):
    def __init__(self, session, authorization_helper):
        self.__session = session
        self.__authorization_helper = authorization_helper
        self.__budget = 500
        self.secret_key = SECRET_KEY
        self.serializer = URLSafeTimedSerializer(self.secret_key)

    def post(self):
        try:
            # get request parameters
            post_data = self.get_args(True)

            with self.__session as session:
                # validation
                validate_email(post_data['email'])
                self.role_validation(post_data['role'])
                self.is_new_user_validation(post_data['email'])

                # get random cards
                card_data_list = asyncio.run(self.generate_player_cards())

                # Hash the password using bcrypt
                hashed_password = self.hash_password(post_data['password'])

                # create new user
                new_user = User(
                    username=post_data['username'],
                    email=post_data['email'],
                    password=hashed_password,
                    country=post_data['country'],
                    role=post_data['role'],
                    budget=self.__budget
                )

                session.add(new_user)
                session.commit()

                # add cards
                for card_data in card_data_list:
                    new_card = Card(
                        name=card_data.get('name', ''),
                        age=card_data.get('age', 0),
                        skill=card_data.get('skill', ''),
                        user_id=new_user.id
                    )
                    session.add(new_card)

                session.commit()

                return {
                    'message': 'User registered successfully',
                    'user_id': new_user.id
                }, 201
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
        except EmailNotValidError as e:
            return {'error': str(e)}, 400
        except Exception as e:
            return {'error': str(e)}, 400

    def get(self, user_id=None):
        try:
            authorized_user = self.__authorization_helper.authorization()

            with self.__session as session:
                # request validation
                self.check_permission(authorized_user, user_id)

                # get users data
                users = []
                if user_id is not None:
                    users.append(self.get_user_by_id(user_id))
                else:
                    # Get query parameters for pagination
                    page = request.args.get('page', default=1, type=int)
                    per_page = request.args.get('per_page', default=2, type=int)

                    users_query = session.query(User)

                    # Calculate the offset based on the page and per_page values
                    offset = (page - 1) * per_page

                    # Perform pagination using limit and offset
                    users = users_query.limit(per_page).offset(offset).all()

                user_data = []
                for user in users:
                    user_cards = session.query(Card).filter_by(user_id=user.id).all()
                    collection_value = sum(card.market_value for card in user_cards)

                    user_data.append({
                        "id": user.id,
                        "username": user.username,
                        "email": user.email,
                        "country": user.country,
                        "role": user.role,
                        "budget": user.budget,
                        "collection_value": collection_value
                    })

                return user_data, 200
        except AuthorizationException as e:
            return {'error': str(e)}, 401
        except PermissionError as e:
            return {'error': str(e)}, 403
        except DataError as e:
            return {'error': str(e)}, 400
        except Exception as e:
            return {'error': str(e)}, 400

    def patch(self, user_id):
        try:
            authorized_user = self.__authorization_helper.authorization()

            with self.__session as session:
                # request validation
                self.check_permission(authorized_user, user_id)

                # get user to update
                user_to_update = self.get_user_by_id(user_id)

                # get request parameters
                patch_data = self.get_args()

                # prepare and validate data to update
                if patch_data['username'] is not None:
                    user_to_update.username = patch_data['username']

                if patch_data['country'] is not None:
                    user_to_update.country = patch_data['country']

                session.commit()

                return {
                    'message': 'User updated successfully',
                }, 201
        except NotFoundException as e:
            return {'error': str(e)}, 404
        except EmailNotValidError as e:
            return {'error': str(e)}, 400
        except AuthorizationException as e:
            return {'error': str(e)}, 401
        except PermissionError as e:
            return {'error': str(e)}, 403
        except Exception as e:
            return {'error': str(e)}, 400

    def delete(self, user_id):
        try:
            authorized_user = self.__authorization_helper.authorization()

            with self.__session as session:
                # request validation
                self.check_permission(authorized_user, user_id)

                # get user to delete
                user_to_delete = self.get_user_by_id(user_id)

                # get cards to delete
                cards_to_delete = session.query(Card).filter_by(user_id=user_id)

                for card in cards_to_delete:
                    session.delete(card)

                session.delete(user_to_delete)
                session.commit()

                return {
                    'message': 'User deleted successfully',
                }, 201
        except AuthorizationException as e:
            return {'error': str(e)}, 401
        except PermissionError as e:
            return {'error': str(e)}, 403
        except NotFoundException as e:
            return {'error': str(e)}, 404
        except Exception as e:
            return {'error': str(e)}, 400

    def check_permission(self, user, user_id):
        # Deny access if not admin and requested another user id
        if not user.role == 'admin' and user.id != user_id:
            raise PermissionError('Forbidden')

    def get_args(self, is_required=False):
        parser = reqparse.RequestParser()
        parser.add_argument('username', required=is_required, help='Username is required')
        parser.add_argument('email', required=is_required, help='Email is required')
        parser.add_argument('password', required=is_required, help='Password is required')
        parser.add_argument('country', required=is_required, help='Country is required')
        parser.add_argument('role', required=is_required, help='Choose your role')
        return parser.parse_args()

    def role_validation(self, role):
        if role not in ['admin', 'regular']:
            raise Exception('Invalid role')

    def is_new_user_validation(self, email):
        if self.__session.query(User).filter(User.email == email).first():
            raise Exception('The user with this email already exists')

    def get_user_by_id(self, user_id):
        user = self.__session.query(User).filter_by(id=user_id).first()
        print(f"user: {user}")
        if user is None:
            raise NotFoundException('No user found')

        return user

    def hash_password(self, password):
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed_password.decode('utf-8')

    async def generate_player_cards(self, num_cards=5, default_skill='5'):
        api_url = "https://apiv3.apifootball.com/?action=get_teams&league_id=" + FOOTBALL_API_LEAGUE_ID + "&APIkey=" + FOOTBALL_API_KEY
        tasks = [asyncio.create_task(self.fetch(api_url))]
        responses = await asyncio.gather(*tasks)

        for response in responses:
            teams_data = json.loads(response)

            if 'error' in teams_data:
                raise CardException('Get Players API returns error')

            # get random team
            random_team = random.choice(teams_data)
            # get players from the chosen team
            team_players = random_team.get('players', [])
            # get random players
            random_players = random.sample(team_players, min(num_cards, len(team_players)))

            cards = []

            for player in random_players:
                skill = player.get('player_rating', '-')
                skill = default_skill if skill == '' else skill
                cards.append({
                    "name": player.get('player_name', 'Noname'),
                    "age": player.get('player_age', '-'),
                    "skill": skill
                })

            return cards

    async def fetch(self, url):
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                return await response.text()
