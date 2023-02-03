from flask import Flask
from flask_cors import CORS
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_socketio import SocketIO
from flask_session import Session

app = Flask(__name__)
CORS(app, supports_credentials=True)

app.config.from_object(Config)

socketio = SocketIO(app, cors_allowed_origins="*")
server_session = Session(app)

db = SQLAlchemy(app)
migrate = Migrate(app, db)

from app import routes, models
