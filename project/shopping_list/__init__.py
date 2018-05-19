from flask import Blueprint

shopping_list = Blueprint(
    'shopping_list',
    __name__,
    template_folder='templates',
    static_folder='static',
)

from . import views
