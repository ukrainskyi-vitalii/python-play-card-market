import requests
import random

from flask_restful import Resource, reqparse
from sqlalchemy.exc import DataError

from config import SECRET_KEY, FOOTBALL_API_LEAGUE_ID, FOOTBALL_API_KEY
from database import Session
from models.card import Card
from models.user import User
from email_validator import validate_email, EmailNotValidError

from itsdangerous import URLSafeTimedSerializer, BadSignature


class UserResource(Resource):
    def __init__(self):
        self.__budget = 500
        self.secret_key = SECRET_KEY
        self.serializer = URLSafeTimedSerializer(self.secret_key)

    def post(self):
        session = Session()

        parser = reqparse.RequestParser()
        parser.add_argument('username', required=True, help='Username is required')
        parser.add_argument('email', required=True, help='Email is required')
        parser.add_argument('country', required=True, help='Country is required')
        parser.add_argument('role', required=True, help='Choose your role')
        args = parser.parse_args()

        username = args['username']
        email = args['email']
        country = args['country']
        role = args['role']

        try:
            validate_email(email)
        except EmailNotValidError:
            return {'error': 'Invalid email format'}, 400

        if role not in ['admin', 'regular']:
            return {'error': 'Invalid role'}, 400

        user = session.query(User).filter(User.email == email).first()
        if user:
            return {'error': 'This email already exists'}, 400

        # get random cards
        card_data_list = self.generate_player_cards()
        print(f"card_data_list: {card_data_list}")
        try:
            # create new user
            new_user = User(
                username=username,
                email=email,
                country=country,
                role=role,
                budget=self.__budget
            )

            session.add(new_user)
            session.commit()

            for card_data in card_data_list:
                new_card = Card(
                    name=card_data.get('name', ''),
                    age=card_data.get('age', 0),
                    skill=card_data.get('skill', ''),
                    user_id=new_user.id
                )
                session.add(new_card)
                session.commit()

            token = self.serializer.dumps({"user_id": new_user.id}, salt="user-salt")

            return {
                'message': 'User registered successfully',
                'user_id': new_user.id,
                'token': token
            }, 201
        except DataError as e:
            session.rollback()
            return {'error': 'DataError: ' + str(e)}, 400


    def get(self, user_id=None):
        session = Session()

        parser = reqparse.RequestParser()
        parser.add_argument('Authorization', location='headers')

        args = parser.parse_args()

        token = args['Authorization']
        if token is None:
            return {'error': 'Empty token'}, 401

        try:
            data = self.serializer.loads(token, salt="user-salt")
            user = session.query(User).filter_by(id=data["user_id"]).first()
        except BadSignature:
            return {'error': 'Invalid token'}, 401

        # Deny access if not admin and requested another user id
        if not user.role == 'admin' and user.id != user_id:
            return {'error': 'Forbidden'}, 403

        users = []
        if user_id is not None:
            user_search = session.query(User).filter_by(id=user_id).first()

            if user_search is None:
                return {'error': 'No user found'}, 404

            users.append(user_search)
        else:
            users = session.query(User).all()

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

        session.close()

        return user_data, 200

    def generate_player_cards(self, num_cards=5):
        api_url = "https://apiv3.apifootball.com/?action=get_teams&league_id="+FOOTBALL_API_LEAGUE_ID+"&APIkey=" + FOOTBALL_API_KEY
        response = requests.get(api_url)
        print(f"response {response}")
        if response.status_code == 200:
            teams_data = response.json()

            if 'error' in teams_data:
                return {'error': teams_data.get('message', 'Get Players API returns error')}, 400

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
            return {'error': 'Get Players API returns error'}, 400
