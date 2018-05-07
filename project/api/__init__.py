from flask import Blueprint

api = Blueprint(
    'api',
    __name__,
    template_folder='templates',
    static_folder='static'
)

from . import views
