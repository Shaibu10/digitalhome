"""
SMS Service Module
Handles SMS communications via mNotify API
"""

from flask import Blueprint

sms_bp = Blueprint('sms', __name__, url_prefix='/admin/sms')

from . import routes