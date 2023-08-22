from flask import Flask
from flask_restful import Api

from database import engine, Base, Session
from helpers.auth import AuthorizationHelper
from resources import UserResource, LoginResource

app = Flask(__name__)
api = Api(app)

session = Session()
authorization_helper = AuthorizationHelper(session)

api.add_resource(UserResource, '/user/<int:user_id>', '/user', resource_class_args=(session, authorization_helper))
api.add_resource(LoginResource, '/login', resource_class_args=(session,))

if __name__ == '__main__':
    Base.metadata.create_all(engine)
    app.run(host='localhost', port=3002, debug=False)
