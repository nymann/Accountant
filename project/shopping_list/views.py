from datetime import date, datetime

from flask import render_template, flash, abort, redirect, url_for
from flask_login import current_user, login_required
from sqlalchemy.exc import DBAPIError

import project
from project.forms import ShoppingForm, ItemForm, NeededItemForm
from project.models import Shopping, User, db, Items, NeededItems
from project.shopping_list import shopping_list
from project.utils.helper import *

from flask_mobility.decorators import mobile_template

@shopping_list.route('/')
@login_required
@mobile_template('shopping_list/{mobile/}index.html')
def index(template):
    form = NeededItemForm()

    shopping_list_entries = Shopping.query.filter(
        Shopping.accounting_id.is_(None)
    ).order_by(Shopping.date.desc()).all()

    needed_items = NeededItems.query.filter(
        NeededItems.item_bought.is_(False)
    ).all()

    return render_template(template, shopping_list_entries=shopping_list_entries,
                           needed_items=needed_items, form=form)


@shopping_list.route('/<shopping_id>')
@login_required
def entry(shopping_id):
    entry = Shopping.query.get_or_404(int(shopping_id))
    return render_template('shopping_list/shopping_entry.html', entry=entry, current_user=current_user, shopping=Shopping)


@shopping_list.route('/new', methods=['GET', 'POST'])
@login_required
def new():
    form = ShoppingForm()

    if form.validate_on_submit():
        user_id = int(form.payee.data) if form.payee.data else current_user.id
        user = User.query.get_or_404(user_id)
        shopping = Shopping(payee_id=user.id, date=datetime.strptime(form.date.data, "%d/%m/%Y"))
        try:
            db.session.add(shopping)
            db.session.commit()
            flash("Success, shopping entry added", "alert alert-info")
            print("Something should appear here")
            return redirect(url_for('shopping_list.items_new', shopping_id=shopping.id))
        except DBAPIError as e:
            flash(str(e), "alert alert-danger")
            db.session.rollback()

    users = User.query.filter(
        User.active
    ).all()

    today = date.today()
    return render_template('shopping_list/new.html', users=users, form=form, today=today)


@shopping_list.route('/edit/<shopping_id>', methods=['GET', 'POST'])
@login_required
def edit(shopping_id):
    form = ShoppingForm()
    shopping = Shopping.query.get_or_404(int(shopping_id))
    if shopping.payee_id is not current_user.id and not is_admin():
        return abort(403)
    if form.validate_on_submit():
        try:
            shopping.payee_id = form.payee.data if (
                    current_user is shopping.payee or current_user.admin) else shopping.payee_id
            shopping.date = datetime.strptime(form.date.data, "%d/%m/%Y")
            db.session.commit()
            flash("Successfully updated shopping entry.", "alert alert-info")
        except (DBAPIError, ValueError) as e:
            flash(str(e), "alert alert-danger")
            db.session.rollback()
    users = User.query.filter(
        User.active
    ).all()
    return render_template('shopping_list/edit.html', shopping=shopping, users=users, form=form)


@shopping_list.route('/delete/<shopping_id>')
@login_required
def delete(shopping_id):
    shopping = Shopping.query.get_or_404(int(shopping_id))
    if current_user is not shopping.payee and not is_admin():
        return abort(403)

    try:
        db.session.delete(shopping)
        db.session.commit()
        flash("Shopping entry removed successfully", "alert alert-info")
    except DBAPIError as e:
        flash(str(e), "alert alert-danger")
        db.session.rollback()
    return redirect(url_for('shopping_list.index'))


@shopping_list.route('/<shopping_id>/items/new', defaults={'edit': False}, methods=['GET', 'POST'])
@shopping_list.route('/<shopping_id>/items/new/<edit>', methods=['GET', 'POST'])
@login_required
def items_new(shopping_id, edit):
    form = ItemForm()
    shopping_entry = Shopping.query.get_or_404(int(shopping_id))
    if form.validate_on_submit():
        needed_item = NeededItems.query.filter(
            NeededItems.item_name == form.name.data
        ).first()
        if needed_item:
            needed_item.item_bought = True

        item = Items(price=float(form.price.data), name=form.name.data, amount=int(form.amount.data),
                     user_id=shopping_entry.payee_id)
        shopping_entry.items.append(item)
        db.session.add(shopping_entry)
        db.session.commit()
        flash("Successfully added item to list", "alert alert-info")
    if edit:
        return redirect(url_for('shopping_list.edit', shopping_id=shopping_id))

    needed_items = NeededItems.query.filter(
        NeededItems.item_bought.is_(False)
    ).all()

    return render_template('shopping_list/new_items.html', shopping=shopping_entry, needed_items=needed_items,
                           form=form)


@shopping_list.route('<int:shopping_id>/items/edit/<int:item_id>', methods=['GET', 'POST'])
def edit_item(shopping_id, item_id):
    form = ItemForm()
    item = Items.query.get_or_404(int(item_id))
    if form.validate_on_submit():
        try:
            item.name = form.name.data
            item.price = form.price.data
            item.amount = form.amount.data
            db.session.commit()
            flash("Successfully edited item.", "alert alert-info")
            return redirect(url_for('shopping_list.edit', shopping_id=shopping_id))
        except DBAPIError as e:
            db.session.rollback()
            project.sentry.captureMessage(str(e))
            flash(str(e), "alert alert-danger")

    return render_template('shopping_list/edit_item.html', item=item, form=form, shopping_id=shopping_id)


@shopping_list.route('<int:shopping_id>/items/delete/<int:item_id>')
def delete_item(shopping_id, item_id):
    item = Items.query.get_or_404(item_id)
    try:
        db.session.delete(item)
        db.session.commit()
        flash("Item deleted successfully.", "alert alert-info")
    except DBAPIError as e:
        flash(str(e), "alert alert-danger")
        project.sentry.captureMessage(str(e))
        db.session.rollback()

    return redirect(url_for('shopping_list.edit', shopping_id=shopping_id))


@shopping_list.route('/needed_item', methods=['GET', 'POST'])
def add_needed_item():
    form = NeededItemForm()
    if form.validate_on_submit():
        item_name = form.item_name.data
        needed_item = NeededItems(item_name=item_name)
        try:
            db.session.add(needed_item)
            db.session.commit()
            flash("Needed item added to list", "alert alert-info")
        except DBAPIError as e:
            flash(str(e), "alert alert-danger")
            project.sentry.captureMessage(str(e))
            db.session.rollback()

    return redirect(url_for('shopping_list.index'))


@shopping_list.route('/removed_item/<needed_item_id>', methods=['GET', 'POST'])
def remove_needed_item(needed_item_id):
    needed_item = NeededItems.query.get_or_404(int(needed_item_id))
    try:
        needed_item.item_bought = True
        db.session.commit()
        flash("Successfully removed needed item.", "alert alert-info")
    except DBAPIError as e:
        project.sentry.captureMessage(str(e))
        flash(str(e), "alert alert-danger")
        db.session.rollback()

    return index()
