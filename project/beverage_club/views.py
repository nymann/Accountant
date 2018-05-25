from project.beverage_club import beverage_club

from flask import render_template


@beverage_club.route('/')
def index():
    # Get the three most sold beers.
    # If no beers are sold, return the latest beers
    return render_template('beverage_club/index.html')
