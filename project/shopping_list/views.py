from flask import render_template, flash, redirect, url_for
from project.shopping_list import shopping_list
from project.models import Shopping, User, db, Items
from project.forms import ShoppingForm, ItemForm
from datetime import date, datetime
from sqlalchemy.exc import DBAPIError


@shopping_list.route('/')
def index():
    shopping_list_entries = Shopping.query.filter(
        Shopping.accounted.is_(False)
    ).all()
    return render_template('shopping_list/index.html', shopping_list_entries=shopping_list_entries)


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


@shopping_list.route('/items/new/<shopping_id>', methods=['GET', 'POST'])
def items_new(shopping_id):
    form = ItemForm()
    shopping_entry = Shopping.query.get_or_404(int(shopping_id))
    if form.validate_on_submit():
        item = Items(price=float(form.price.data), name=form.name.data, amount=int(form.amount.data),
                     user_id=shopping_entry.payee_id)
        shopping_entry.items.append(item)
        db.session.add(shopping_entry)
        db.session.commit()

    return render_template('shopping_list/new_items.html', shopping_entry=shopping_entry, form=form)
