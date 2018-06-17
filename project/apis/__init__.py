from flask import Blueprint

apis = Blueprint(
    'beverage_club_api',
    __name__,
    template_folder='templates',
    static_folder='static',
)

from . import beverage_club_api
