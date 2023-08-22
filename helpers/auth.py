from flask_restful import reqparse
from config import SECRET_KEY
from exceptions.authorization_exception import AuthorizationException
from itsdangerous import BadSignature, URLSafeTimedSerializer
from models.user import User


class AuthorizationHelper:
    def __init__(self, session):
        self.__session = session
        self.serializer = URLSafeTimedSerializer(SECRET_KEY)

    def authorization(self):
        parser = reqparse.RequestParser()
        parser.add_argument('Authorization', location='headers')

        args = parser.parse_args()

        token = args['Authorization']
        if token is None:
            raise AuthorizationException('Empty token')

        try:
            with self.__session as session:
                data = self.serializer.loads(token, salt="user-salt")
                user = session.query(User).filter_by(id=data["user_id"]).first()
                if user is None:
                    raise AuthorizationException('User not found')

                return user
        except BadSignature:
            raise AuthorizationException('Invalid token')
