from flask import Flask
from config import Config

# Create the Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Import routes at the end to avoid circular imports
from app import routes