from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_mail import Mail
from dotenv import load_dotenv
from .routes import register_blueprints



load_dotenv()

db = SQLAlchemy()
mail = Mail()


def create_app():
    app = Flask(__name__)
    CORS(app)

    app.config.from_object('app.config.Config')

    db.init_app(app)
    mail.init_app(app)

    register_blueprints(app)

   
    return app
