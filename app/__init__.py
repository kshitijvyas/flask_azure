from flask import Flask
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
import os
from app.database import db
from app.serializers import ma
from app.config import get_config


def create_app():
    app = Flask(__name__)
    
    # Load configuration based on FLASK_ENV
    app.config.from_object(get_config())

    # Initialize Application Insights (Monitoring)
    appinsights_connection_string = os.environ.get('APPLICATIONINSIGHTS_CONNECTION_STRING')
    if appinsights_connection_string:
        from opencensus.ext.azure.log_exporter import AzureLogHandler
        from opencensus.ext.flask.flask_middleware import FlaskMiddleware
        
        # Add Flask middleware for automatic request tracking
        middleware = FlaskMiddleware(
            app,
            exporter=AzureLogHandler(connection_string=appinsights_connection_string)
        )
        
        # Configure logging
        import logging
        logger = logging.getLogger(__name__)
        logger.addHandler(AzureLogHandler(connection_string=appinsights_connection_string))
        logger.setLevel(logging.INFO)
        app.logger.info("Application Insights enabled")

    # Initialize extensions
    db.init_app(app)
    ma.init_app(app)
    
    # Import models BEFORE initializing Migrate (critical for migrations to detect models)
    from app import models
    
    Migrate(app, db)

    # Create tables
    with app.app_context():
        db.create_all()

    # Register blueprints from routers
    from app.routers.user_router import user_bp
    from app.routers.department_router import department_bp
    from app.routers.salary_router import salary_bp
    from app.routers.attendance_router import attendance_bp
    
    app.register_blueprint(user_bp, url_prefix='/api')
    app.register_blueprint(department_bp, url_prefix='/api')
    app.register_blueprint(salary_bp, url_prefix='/api')
    app.register_blueprint(attendance_bp, url_prefix='/api')

    return app
