def register_blueprints(app):
    from .auth_routes import auth_bp
    from .admin_routes import admin_bp
    from .doctor_routes import doctor_bp
    from .prediction import prediction_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(doctor_bp)
    app.register_blueprint(prediction_bp)
