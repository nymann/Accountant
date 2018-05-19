from flask import render_template
from project.shopping_list import shopping_list
from project.models import Shopping


@shopping_list.route('/')
def index():
    shopping_list_entries = Shopping.query.filter(
        Shopping.accounted.is_(False)
    ).all()
    return render_template('shopping_list/index.html', shopping_list_entries=shopping_list_entries)
