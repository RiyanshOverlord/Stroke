from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_cors import CORS
from dotenv import load_dotenv
from app import create_app, db


mail = Mail()
s = None  

# This function sets the global serialize
def set_serializer_secret(app):
    global s
    from itsdangerous import URLSafeTimedSerializer
    s = URLSafeTimedSerializer(app.config['SECRET_KEY'])

# Blueprints and config
from app.config import DevelopmentConfig
from app.routes.doctor_routes import doctor_bp
from app.routes.prediction import prediction_bp
from app.routes.auth_routes import auth_bp
from app.routes.admin_routes import admin_bp

def create_app():
    app = Flask(__name__)
    CORS(app)
    load_dotenv()

    app.config.from_object(DevelopmentConfig)

    db.init_app(app)
    mail.init_app(app)
    set_serializer_secret(app)  

    app.register_blueprint(doctor_bp)
    app.register_blueprint(prediction_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)

    return app

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)
