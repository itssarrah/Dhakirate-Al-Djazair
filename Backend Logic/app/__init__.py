from flask import Flask
from flask_cors import CORS
from .config import Config
import os


def create_app():
    app = Flask(__name__)
    CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})
    CORS(app)

    # Load configuration
    app.config.from_object(Config)

    # Import and register routes
    from . import routes
    app.register_blueprint(routes.bp)

    return app
