from flask import Blueprint

api = Blueprint('api', __name__)

from . import authentication, closets, decorators, errors, groups, items, packing_lists, users
