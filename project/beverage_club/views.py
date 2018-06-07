from flask_login import login_required

from project.beverage_club import beverage_club
from sqlalchemy.exc import DBAPIError

from flask import render_template, flash, redirect, url_for
from project.forms import NewBeverageForm, NewBeverageBatchForm, BuyBeverageForm, NewBeverageTypesForm
from project.models import Beverage, BeverageBatch, BeverageUser, BeverageTypes, db, User
from project.utils.decorators import *
from project.utils.helper import *


@beverage_club.route('/')
@login_required
def index():
    form = BuyBeverageForm()

    users = User.query.filter(
        User.active
    ).all()

    beverages = db.session.query(
        Beverage.name.label('name'), Beverage.id.label('id')
    ).join(BeverageBatch).filter(
        BeverageBatch.quantity > 0
    ).order_by(
        Beverage.name
    ).distinct()

    beverage_types = BeverageTypes.query.all()


    return render_template('beverage_club/index.html', beverages=beverages,
                           beverage_types=beverage_types, users=users, form=form)


@beverage_club.route('/admin_module', methods=['GET', 'POST'])
@login_required
def admin_module():
    form_beverage = NewBeverageForm()
    form_beverage_type = NewBeverageTypesForm()

    beverages = Beverage.query.all()
    beverage_types = BeverageTypes.query.all()

    if len(beverage_types) == 0:
        flash("There are no beverage types. Go create on.", "alert alert-danger")

    return render_template('beverage_club/admin_module.html', form_beverage=form_beverage,
                           form_beverage_type=form_beverage_type, beverages=beverages,
                           beverage_types=beverage_types)


@beverage_club.route('/new', methods=['GET', 'POST'])
@login_required
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

        # type cannot be blank
        if type.lstrip() == "":
            flash("Beverage type must be selected", "alert alert-danger")
            return redirect(url_for('beverage_club.admin_module'))
        print(type)

        # checks if beverage already exists
        name_db = Beverage.query.filter(
            Beverage.name == name
        ).first()
        if name_db:
            flash("Beverage already exists", "alert alert-danger")
            return redirect(url_for('beverage_club.admin_module'))

        beverage = Beverage(name=name, type=type, contents=contents)

        try:
            db.session.add(beverage)
            db.session.commit()
            flash("Beverage added successfully", "alert alert-info")
            return redirect(url_for('beverage_club.index'))
        except DBAPIError as e:
            db.session.rollback()
            flash(str(e), "alert alert-danger")

    return admin_module


@beverage_club.route('/new_type', methods=['GET', 'POST'])
@login_required
def new_beverage_type():
    form = NewBeverageTypesForm()

    if form.validate_on_submit():
        type = form.type_new.data

        # checks if beverage type already exists
        type_db = BeverageTypes.query.filter(
            BeverageTypes.type == type
        ).first()
        if type_db:
            flash("Beverage Type already exists", "alert alert-danger")
            return redirect(url_for('beverage_club.admin_module'))

        beverage_type = BeverageTypes(type=type)

        try:
            db.session.add(beverage_type)
            db.session.commit()
            flash("Beverage Type added successfully", "alert alert-info")
            return redirect(url_for('beverage_club.index'))
        except DBAPIError as e:
            db.session.rollback()
            flash(str(e), "alert alert-danger")

    return admin_module


@beverage_club.route('/beverage/<int:user_id>', methods=['GET', 'POST'])
@login_required
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
            beverage_batch.quantity -= 1

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
@active
def new_beverage_batch():
    form = NewBeverageBatchForm()
    beverages = Beverage.query.all()
    users = User.query.filter(
        User.active
    ).all()

    if beverages:
        if form.validate_on_submit():
            payee_id = form.payee.data if form.payee.data else current_user.id
            try:
                beverage_id = form.beverage_id.data
                quantity = int(form.quantity.data)
                price_per_can = float(form.price.data) / quantity

            except ValueError as e:
                flash(str(e), "alert alert-danger")
                return redirect(url_for('beverage_club.new_beverage_batch'))

            beverage_batch = BeverageBatch(
                beverage_id=beverage_id, quantity=quantity, price_per_can=price_per_can, payee_id=payee_id)

            try:
                db.session.add(beverage_batch)
                db.session.commit()
                flash("Beverage Batch added succesfully")
                return redirect(url_for('beverage_club.index'))
            except DBAPIError as e:
                db.session.rollback()
                flash(str(e), "alert alert-danger")
    else:
        flash("There is no beverages created. Contact an admin.", "alert alert-danger")

    return render_template('beverage_club/beverage_batch_old.html', form=form, beverages=beverages, users=users)
