import requests
import random

from flask_restful import Resource, reqparse
from sqlalchemy.exc import DataError

from config import SECRET_KEY, FOOTBALL_API_LEAGUE_ID, FOOTBALL_API_KEY
from database import Session
from exceptions.authorization_exception import AuthorizationException
from exceptions.card_exception import CardException
from exceptions.not_found_exception import NotFoundException
from models.card import Card
from models.user import User
from email_validator import validate_email, EmailNotValidError

from itsdangerous import URLSafeTimedSerializer, BadSignature


class UserResource(Resource):
    def __init__(self):
        self.__session = Session()
        self.__budget = 500
        self.secret_key = SECRET_KEY
        self.serializer = URLSafeTimedSerializer(self.secret_key)

    def post(self):
        try:
            # get request parameters
            post_data = self.get_args(True)

            # validation
            validate_email(post_data['email'])
            self.role_validation(post_data['role'])
            self.is_new_user_validation(post_data['email'])

            # get random cards
            card_data_list = self.generate_player_cards()

            # create new user
            new_user = User(
                username=post_data['username'],
                email=post_data['email'],
                country=post_data['country'],
                role=post_data['role'],
                budget=self.__budget
            )

            self.__session.add(new_user)
            self.__session.commit()

            # add cards
            for card_data in card_data_list:
                new_card = Card(
                    name=card_data.get('name', ''),
                    age=card_data.get('age', 0),
                    skill=card_data.get('skill', ''),
                    user_id=new_user.id
                )
                self.__session.add(new_card)
                self.__session.commit()

            token = self.serializer.dumps({"user_id": new_user.id}, salt="user-salt")

            self.__session.close()

            return {
                'message': 'User registered successfully',
                'user_id': new_user.id,
                'token': token
            }, 201
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
            authorized_user = self.authorization()

            # request validation
            self.check_permission(authorized_user, user_id)

            # get users data
            users = []
            if user_id is not None:
                users.append(self.get_user_by_id(user_id))
            else:
                users = self.__session.query(User).all()

            user_data = []
            for user in users:
                user_data.append({
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "country": user.country,
                    "role": user.role,
                    "budget": user.budget
                })

            self.__session.close()

            return user_data, 200
        except AuthorizationException as e:
            return {'error': str(e)}, 401
        except DataError as e:
            return {'error': str(e)}, 400
        except Exception as e:
            return {'error': str(e)}, 400

    def patch(self, user_id):
        try:
            authorized_user = self.authorization()

            # request validation
            self.check_permission(authorized_user, user_id)

            # get user to update
            user_to_update = self.get_user_by_id(user_id)

            # get request parameters
            patch_data = self.get_args()

            # prepare and validate data to update
            if patch_data['username'] is not None:
                user_to_update.username = patch_data['username']

            if patch_data['email'] is not None:
                validate_email(patch_data['email'])
                self.is_new_user_validation(patch_data['email'])
                user_to_update.email = patch_data['email']

            if patch_data['country'] is not None:
                user_to_update.country = patch_data['country']

            if patch_data['role'] is not None:
                self.role_validation(patch_data['role'])
                user_to_update.role = patch_data['role']

            self.__session.commit()
            self.__session.close()

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
            authorized_user = self.authorization()

            # request validation
            self.check_permission(authorized_user, user_id)

            # get user to delete
            user_to_delete = self.get_user_by_id(user_id)

            self.__session.delete(user_to_delete)
            self.__session.commit()
            self.__session.close()

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

    def authorization(self):
        parser = reqparse.RequestParser()
        parser.add_argument('Authorization', location='headers')

        args = parser.parse_args()

        token = args['Authorization']
        if token is None:
            raise AuthorizationException('Empty token')

        try:
            data = self.serializer.loads(token, salt="user-salt")
            user = self.__session.query(User).filter_by(id=data["user_id"]).first()
            if user is None:
                raise AuthorizationException('User not found')

            return user
        except BadSignature:
            raise AuthorizationException('Invalid token')

    def check_permission(self, user, user_id):
        # Deny access if not admin and requested another user id
        if not user.role == 'admin' and user.id != user_id:
            raise PermissionError('Forbidden')

    def get_args(self, is_required=False):
        parser = reqparse.RequestParser()
        parser.add_argument('username', required=is_required, help='Username is required')
        parser.add_argument('email', required=is_required, help='Email is required')
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

        if user is None:
            raise NotFoundException('No user found')

        return user

    def generate_player_cards(self, num_cards=5):
        api_url = "https://apiv3.apifootball.com/?action=get_teams&league_id=" + FOOTBALL_API_LEAGUE_ID + "&APIkey=" + FOOTBALL_API_KEY
        response = requests.get(api_url)

        if response.status_code == 200:
            teams_data = response.json()

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
                cards.append({
                    "name": player.get('player_name', 'Noname'),
                    "age": player.get('player_age', '-'),
                    "skill": player.get('player_rating', '-')
                })

            return cards
        else:
            raise CardException('Get Players API returns error')
