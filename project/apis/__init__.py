from flask import Blueprint
from flask_restplus import Api

api_blueprint = Blueprint(
    'beverage_club_api',
    __name__
)

api = Api(api_blueprint)

from . import beverage_club_api
