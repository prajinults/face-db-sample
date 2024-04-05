from flask import Blueprint, jsonify
from werkzeug.utils import import_string
from core.fn import get_all_modules
from os.path import dirname
from logging import getLogger 
logger = getLogger(__name__)
 
modules = get_all_modules(dirname(__file__), version="v1")

api_v1_bp = Blueprint('api_v1_bp', __name__, url_prefix='/api/v1')


logger.info('Loaded module ')
for module in modules:
    blue_print = import_string(module)
    logger.info(module)
    api_v1_bp.register_blueprint(blue_print)


