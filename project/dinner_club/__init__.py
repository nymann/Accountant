from flask import Blueprint

dinner_club = Blueprint(
    'dinner_club',
    __name__,
    template_folder='templates',
    static_folder='static',
)

from . import views
