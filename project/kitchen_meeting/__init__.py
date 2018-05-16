from flask import Blueprint

kitchen_meeting = Blueprint(
    'kitchen_meeting',
    __name__,
    template_folder='templates',
    static_folder='static',
)

from . import views
