from project.beverage_club import beverage_club

from flask import render_template
from project.forms import NewBeverageForm

@beverage_club.route('/')
def index():
    # Get the three most sold beers.
    # If no beers are sold, return the latest beers
    return render_template('beverage_club/index.html')


@beverage_club.route('/new')
def new_beverage():
    form = NewBeverageForm
    return render_template('beverage_club/new_beverage.html', form=form)
