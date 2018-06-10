from flask import Blueprint

feedback = Blueprint(
    'feedback',
    __name__,
    template_folder='templates',
    static_folder='static',
)

from . import views
