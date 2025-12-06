# auth/__init__.py
from flask import Blueprint

# Create auth blueprint
auth_bp = Blueprint('auth', __name__, template_folder='templates/auth')

# Import routes after creating blueprint to avoid circular imports
from . import routes