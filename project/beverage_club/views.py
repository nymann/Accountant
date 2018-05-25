from project.beverage_club import beverage_club

from flask import render_template


@beverage_club.route('/')
def index():
    return render_template('beverage_club/index.html')
