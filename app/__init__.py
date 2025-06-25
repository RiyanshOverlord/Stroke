from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_mail import Mail
from dotenv import load_dotenv
from itsdangerous import URLSafeTimedSerializer


load_dotenv()

db = SQLAlchemy()
mail = Mail()
s = None

def set_serializer_secret(app):
    global s
    s = URLSafeTimedSerializer(app.config['SECRET_KEY'])

def create_app():
    app = Flask(__name__)
    CORS(app)

    app.config.from_object('app.config.Config')

    db.init_app(app)
    mail.init_app(app)

    from .routes import register_blueprints
    register_blueprints(app)

    with app.app_context():
        db.create_all()

    return app
