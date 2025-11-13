from flask import Flask
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
import os
import logging
from app.database import db
from app.serializers import ma
from app.config import get_config


def create_app():
    app = Flask(__name__)
    
    # Load configuration based on FLASK_ENV
    app.config.from_object(get_config())
    
    # Configure logging to ensure it appears in Azure Log Stream
    logging.basicConfig(
        level=logging.INFO,
        format='%(levelname)s - %(name)s - %(message)s'
    )
    
    # Set Flask app logger level
    app.logger.setLevel(logging.INFO)

    # Initialize Application Insights (Monitoring) with OpenTelemetry
    appinsights_connection_string = os.environ.get('APPLICATIONINSIGHTS_CONNECTION_STRING')
    if appinsights_connection_string:
        from azure.monitor.opentelemetry import configure_azure_monitor
        from opentelemetry.instrumentation.flask import FlaskInstrumentor
        
        # Configure Azure Monitor with OpenTelemetry
        configure_azure_monitor(connection_string=appinsights_connection_string)
        
        # Instrument Flask for automatic request tracking
        FlaskInstrumentor().instrument_app(app)
        
        app.logger.info("Application Insights enabled with OpenTelemetry")

    # Initialize extensions
    db.init_app(app)
    ma.init_app(app)
    jwt = JWTManager(app)
    
    # Import models BEFORE initializing Migrate (critical for migrations to detect models)
    from app import models
    
    Migrate(app, db)

    # Create tables
    with app.app_context():
        db.create_all()

    # Register blueprints from routers
    from app.routers.auth_router import auth_bp
    from app.routers.user_router import user_bp
    from app.routers.department_router import department_bp
    from app.routers.salary_router import salary_bp
    from app.routers.attendance_router import attendance_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api')
    app.register_blueprint(user_bp, url_prefix='/api')
    app.register_blueprint(department_bp, url_prefix='/api')
    app.register_blueprint(salary_bp, url_prefix='/api')
    app.register_blueprint(attendance_bp, url_prefix='/api')
    
    # JWT error handlers
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return {'error': 'Token has expired', 'message': 'Please login again'}, 401
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return {'error': 'Invalid token', 'message': 'Token verification failed'}, 401
    
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return {'error': 'Authorization required', 'message': 'Request does not contain an access token'}, 401

    return app
