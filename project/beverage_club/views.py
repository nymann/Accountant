from project.beverage_club import beverage_club
from sqlalchemy.exc import DBAPIError

from flask import render_template, flash, redirect, url_for
from project.forms import NewBeverageForm
from project.models import Beverage, db


@beverage_club.route('/')
def index():
    # Get the three most sold beers.
    # If no beers are sold, return the latest beers
    return render_template('beverage_club/index.html')


@beverage_club.route('/new', methods=['GET', 'POST'])
def new_beverage():
    form = NewBeverageForm()

    if form.validate_on_submit():
        try:
            contents = float(form.contents.data)
        except ValueError as e:
            flash(str(e), 'alert alert-danger')
            return redirect(url_for('dinner_club.new'))

        name = form.name.data
        type = form.type.data

        beverage = Beverage(name=name, type=type, contents=contents)

        try:
            db.session.add(beverage)
            db.session.commit()
            flash("Beverage added successfully", "alert alert-info")
            return redirect(url_for('beverage_club.index'))
        except DBAPIError as e:
            db.session.rollback()
            flash("str(e)", "alert alert-danger")

    return render_template('beverage_club/new_beverage.html', form=form)
