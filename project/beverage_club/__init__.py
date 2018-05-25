from flask import Blueprint

beverage_club = Blueprint(
    'beverage_club',
    __name__,
    template_folder='templates',
    static_folder='static',
)

from . import views
