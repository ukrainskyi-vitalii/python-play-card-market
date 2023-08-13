from flask import Flask
from flask_restful import Api

from database import engine, Base
from resources import UserResource

app = Flask(__name__)
api = Api(app)

api.add_resource(UserResource, '/user')

if __name__ == '__main__':
    Base.metadata.create_all(engine)
    app.run(host='localhost', port=3000, debug=False)
