from flask_restful import Resource, reqparse
from sqlalchemy.exc import DataError

from database import Session
from models.user import User
from email_validator import validate_email, EmailNotValidError


class UserResource(Resource):
    def __init__(self):
        self.__budget = 500

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

        user = session.query(User).filter(User.username == username, User.email == email).first()
        if user:
            return {'error': 'Username already exists'}, 400

        new_user = User(
            username=username,
            email=email,
            country=country,
            role=role,
            budget=self.__budget
        )

        try:
            session.add(new_user)
            session.commit()
        except DataError as e:
            session.rollback()
            return {'error': 'DataError: ' + str(e)}, 400

        return {
            'message': 'User registered successfully',
            'user_id': new_user.id
        }, 201
