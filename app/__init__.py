# app/__init__.py
from flask import Flask
import os

def create_app():
    app = Flask(__name__, static_folder='../public', static_url_path='')
    
    # Register blueprints
    from .routes import api
    app.register_blueprint(api, url_prefix='/api')
    
    return app