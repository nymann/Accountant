from project.beverage_club import beverage_club
from sqlalchemy.exc import DBAPIError

from flask import render_template, flash, redirect, url_for
from project.forms import NewBeverageForm, NewBeverageBatchForm, BuyBeverageForm, NewBeverageTypesForm
from project.models import Beverage, BeverageBatch, BeverageUser, BeverageTypes, db


@beverage_club.route('/')
def index():
    form = BuyBeverageForm()

    beverages = db.session.query(
        Beverage.name.label('name'), Beverage.id.label('id')
    ).join(BeverageBatch).filter(BeverageBatch.quantity > 0).order_by(Beverage.name).all()

    # Get the three most sold beers.

    # If no beers are sold, return the latest beers

    return render_template('beverage_club/index.html', beverages=beverages, form=form)


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
            flash(str(e), "alert alert-danger")

    return render_template('beverage_club/new_beverage.html', form=form)


@beverage_club.route('/new_type', methods=['GET', 'POST'])
def new_beverage_type():
    form = NewBeverageTypesForm()

    if form.validate_on_submit():
        type = form.type.data

        beverage_type = BeverageTypes(type=type)

        try:
            db.session.add(beverage_type)
            db.session.commit()
            flash("Beverage Type added successfully", "alert alert-info")
            return redirect(url_for('beverage_club.index'))
        except DBAPIError as e:
            db.session.rollback()
            flash(str(e), "alert alert-danger")

    return render_template('beverage_club/new_beverage_type.html', form=form)


@beverage_club.route('/beverage/<int:user_id>', methods=['GET', 'POST'])
def buy_beverage(user_id):
    form = BuyBeverageForm()
    if form.validate_on_submit():
        beverage_id = form.beverage_id.data

        # getting beverage_batch with beverage_id
        beverage_batch = BeverageBatch.query.filter(
            BeverageBatch.quantity != 0
        ).filter_by(
            beverage_id=beverage_id
        ).first()

        try:
            # decrementing quantity
            beverage_batch.quantity = beverage_batch.quantity - 1

            # assigning beer
            bought_beverage = BeverageUser(beverage_batch_id=beverage_batch.id, user_id=user_id)
            db.session.add(bought_beverage)
            db.session.commit()
            flash("Successfully bought a beverage", "alert alert-info")
        except DBAPIError as e:
            db.session.rollback()
            flash(str(e), "alert alert-danger")

    return index()


@beverage_club.route('/beverage_batch', methods=['GET', 'POST'])
def new_beverage_batch():
    form = NewBeverageBatchForm()
    beverages = Beverage.query.all()

    if form.validate_on_submit():
        try:
            beverage_id = form.beverage_id.data
            quantity = int(form.quantity.data)
            price_per_can = float(form.price.data) / quantity

        except ValueError as e:
            flash(str(e), "alert alert-danger")
            redirect(url_for('beverage_club.new_beverage_batch'))

        beverage_batch = BeverageBatch(beverage_id=beverage_id, quantity=quantity, price_per_can=price_per_can)

        try:
            db.session.add(beverage_batch)
            db.session.commit()
            flash("Beverage Batch added succesfully")
            return redirect(url_for('beverage_club.index'))
        except DBAPIError as e:
            db.session.rollback()
            flash(str(e), "alert alert-danger")

    return render_template('beverage_club/beverage_batch.html', form=form, beverages=beverages)
