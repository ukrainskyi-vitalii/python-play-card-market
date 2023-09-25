import bcrypt
from flask_restful import Resource, reqparse
from sqlalchemy.exc import DataError

from config import SECRET_KEY
from models.user import User

from itsdangerous import URLSafeTimedSerializer

from werkzeug.exceptions import HTTPException


class LoginResource(Resource):
    def __init__(self, session):
        self.__session = session
        self.serializer = URLSafeTimedSerializer(SECRET_KEY)

    def post(self):
        try:
            # get request parameters
            post_data = self.get_args()

            with self.__session as session:
                # Get user by email
                user = session.query(User).filter_by(email=post_data['email']).first()
                if user is None:
                    raise PermissionError('Forbidden')

                # validate password
                if not bcrypt.checkpw(post_data['password'].encode('utf-8'), user.password.encode('utf-8')):
                    raise PermissionError('Forbidden')

                token = self.serializer.dumps({"user_id": user.id}, salt="user-salt")

                return {
                    'message': 'success',
                    'token': token
                }, 201
        except HTTPException as e:
            if hasattr(e, 'data'):
                return {'error': e.data.get('message', str(e))}, 400
            else:
                return {'error': str(e)}, 400
        except PermissionError as e:
            return {'error': str(e)}, 404
        except DataError as e:
            return {'error': str(e)}, 400
        except Exception as e:
            return {'error': str(e)}, 400

    def get_args(self):
        parser = reqparse.RequestParser()
        parser.add_argument('email', required=True, help='Email is required')
        parser.add_argument('password', required=True, help='Password is required')
        return parser.parse_args()
