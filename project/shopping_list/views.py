from flask import render_template, flash, abort, request, redirect, url_for
from flask_login import current_user
from project.shopping_list import shopping_list
from project.models import Shopping, User, db, Items, NeededItems
from project.forms import ShoppingForm, ItemForm, NeededItemForm
from datetime import date, datetime
from sqlalchemy.exc import DBAPIError


@shopping_list.route('/')
def index():
    form = NeededItemForm()
    shopping_list_entries = Shopping.query.filter(
        Shopping.accounted.is_(False)
    ).all()
    needed_items = NeededItems.query.filter(
        NeededItems.item_bought.is_(False)
    ).all()
    return render_template('shopping_list/index.html', shopping_list_entries=shopping_list_entries,
                           needed_items=needed_items, form=form)


@shopping_list.route('/<shopping_id>')
def entry(shopping_id):
    entry = Shopping.query.get_or_404(int(shopping_id))
    return render_template('shopping_list/shopping_entry.html', entry=entry)


@shopping_list.route('/new', methods=['GET', 'POST'])
def new():
    form = ShoppingForm()

    if form.validate_on_submit():
        user = User.query.get_or_404(int(form.payee.data))
        shopping = Shopping(payee_id=user.id, date=datetime.strptime(form.date.data, "%d/%m/%Y"))
        try:
            db.session.add(shopping)
            db.session.commit()
            flash("Success, shopping entry added", "alert alert-info")
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
def edit(shopping_id):
    form = ShoppingForm()
    shopping = Shopping.query.get_or_404(int(shopping_id))
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
def delete(shopping_id):
    shopping = Shopping.query.get_or_404(int(shopping_id))
    if current_user is not shopping.payee and not current_user.admin:
        return abort(502)

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
def items_new(shopping_id, edit):
    form = ItemForm()
    shopping_entry = Shopping.query.get_or_404(int(shopping_id))
    if form.validate_on_submit():
        item = Items(price=float(form.price.data), name=form.name.data, amount=int(form.amount.data),
                     user_id=shopping_entry.payee_id)
        shopping_entry.items.append(item)
        db.session.add(shopping_entry)
        db.session.commit()
    if edit:
        return redirect(url_for('shopping_list.edit', shopping_id=shopping_id))

    needed_items = NeededItems.query.filter(
        NeededItems.item_bought == False
    ).all()

    return render_template('shopping_list/new_items.html', shopping=shopping_entry, needed_items=needed_items,
                           form=form)


@shopping_list.route('<int:shopping_id>/items/edit/<int:item_id>', methods=['GET', 'POST'])
def edit_item(shopping_id, item_id):
    form = ItemForm()
    print(shopping_id)
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
        db.session.rollback()

    return redirect(url_for('shopping_list.edit', shopping_id=shopping_id))


@shopping_list.route('/needed_item', methods=['GET', 'POST'])
def add_needed_item():
    form = NeededItemForm()
    if form.validate_on_submit():
        item_name = form.name.data
        needed_item = NeededItems(item_name=item_name)
        try:
            db.session.add(needed_item)
            db.session.commit()
            flash("Needed item added to list", "alert alert-info")
        except DBAPIError as e:
            flash(str(e), "alert alert-danger")
            db.session.rollback()

    return index()
