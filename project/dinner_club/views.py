from datetime import datetime

from flask import render_template, redirect, url_for, flash, request
from flask_login import current_user
from sqlalchemy.exc import DBAPIError

from project.dinner_club import dinner_club
from project.forms import DinnerForm
from project.models import User, Dinner
from project.models import db


@dinner_club.route('/new', methods=['GET', 'POST'])
def new():
    # active_dinner_club_participants
    users = User.query.filter(
        User.subscribed_to_dinner_club,
        User.active
    ).all()

    form = DinnerForm(participants=users)

    if form.validate_on_submit():
        payee_id = form.payee.data if form.payee.data else current_user.id
        dish_name = form.dish_name.data
        # value checker
        try:
            price = float(form.price.data)
        except ValueError as e:
            flash(str(e), 'alert alert-danger')
            return redirect(url_for('dinner_club.new'))
        # price = float(form.price.data)
        date = datetime.strptime(form.date.data, "%d/%m/%Y").date()

        participants = list()
        for user_id in request.form.getlist('participants'):
            participants.append(User.query.get(int(user_id)))

        guests = list()
        for guest in form.guests.data.splitlines():
            if guest.isspace():
                break
            user = User.query.filter(
                User.name == guest
            ).first()
            if user:
                guests.append(user)
            else:
                flash("Couldn't find guest with name {0}. Are you sure it's correct?".format(guest))
                return redirect(url_for('dinner_club.new'))

        chefs = list()
        for user_id in request.form.getlist('chefs'):
            chefs.append(User.query.get(int(user_id)))

        try:
            dinner = Dinner(payee_id=payee_id, price=price, date=date, participants=participants, guests=guests,
                            chefs=chefs, dish_name=dish_name)
            db.session.add(dinner)
            db.session.commit()
            flash("Success", "alert alert-info")
            return redirect(url_for('dinner_club.index'))
        except DBAPIError as e:
            flash(str(e), "alert alert-danger")

    return render_template('dinner_club/new.html', form=form, users=users)


@dinner_club.route('/')
def index():
    query = Dinner.query.filter(
        Dinner.accounted.is_(False)
    )

    latest_dinner = query.first()
    dinners = query.all()

    return render_template('dinner_club/index.html', dinners=dinners, latest_dinner=latest_dinner)


@dinner_club.route('/meal/<dinner_id>')
def meal(dinner_id):
    dinner = Dinner.query.get_or_404(int(dinner_id))
    return render_template('dinner_club/meal.html', dinner=dinner)
