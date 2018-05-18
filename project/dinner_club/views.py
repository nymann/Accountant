from collections import Counter
from datetime import datetime

from flask import render_template, redirect, url_for, flash, request
from flask_login import current_user
from sqlalchemy.exc import DBAPIError
from sqlalchemy.sql import label

from project.dinner_club import dinner_club
from project.forms import DinnerForm
from project.models import User, Dinner, GuestAssociation
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
        # TODO(CHECK IF USER IS ADMIN, IF form.payee.data)
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

        chefs = list()
        for user_id in request.form.getlist('chefs'):
            chefs.append(User.query.get(int(user_id)))

        try:
            d = Dinner(payee_id=payee_id, price=price, date=date, participants=participants, chefs=chefs,
                       dish_name=dish_name)
            g = Counter(form.guests.data.splitlines())
            if form.guests.data is None or str(form.guests.data).isspace() or str(form.guests.data) is "":
                db.session.add(d)
                db.session.commit()
                flash("Success", "alert alert-info")
                return redirect(url_for('dinner_club.index'))
            with db.session.no_autoflush:
                for key in g:
                    if key.isspace():
                        break
                    user = User.query.filter(
                        User.name == key
                    ).first()
                    if user:
                        numbers = g[key]
                        try:
                            ga = GuestAssociation(number_of_guests=numbers)
                            ga.user = user
                            d.guests.append(ga)
                            db.session.add(d)
                            db.session.commit()
                        except DBAPIError as e:
                            print(str(e))
                            db.session.rollback()
                    else:
                        flash("Couldn't find guest with name {0}. Are you sure it's correct?".format(key))
                        return redirect(url_for('dinner_club.new'))
            flash("Success", "alert alert-info")
            return redirect(url_for('dinner_club.index'))
        except DBAPIError as e:
            flash(str(e), "alert alert-danger")

    return render_template('dinner_club/new.html', form=form, users=users)


@dinner_club.route('/')
def index():
    latest_dinner = Dinner.query.filter(
        Dinner.accounted.is_(False)
    ).order_by(
        Dinner.date.desc()
    ).first()

    dinners = Dinner.query.filter(
        Dinner.accounted.is_(False)
    ).order_by(
        Dinner.date.desc()
    ).all()

    return render_template('dinner_club/index.html', dinners=dinners, latest_dinner=latest_dinner)


@dinner_club.route('/meal/<dinner_id>')
def meal(dinner_id):
    dinner = Dinner.query.get_or_404(int(dinner_id))
    return render_template('dinner_club/meal.html', dinner=dinner)


@dinner_club.route('/meal/edit/<dinner_id>', methods=['GET', 'POST'])
def edit(dinner_id):
    form = DinnerForm()
    dinner = Dinner.query.get(int(dinner_id))
    if form.validate_on_submit():
        try:
            price = float(form.price.data)
        except ValueError as e:
            flash(str(e), 'alert alert-danger')
            return redirect(url_for('dinner_club.new'))
        dinner.price = price
        dinner.dish_name = form.dish_name.data
        dinner.date = datetime.strptime(form.date.data, "%d/%m/%Y")
        dinner.payee_id = form.payee.data if current_user.admin else dinner.payee_id

        # Participants
        dinner.participants = []
        for user_id in request.form.getlist('participants'):
            dinner.participants.append(User.query.get(int(user_id)))

        # Chefs
        dinner.chefs = []
        for user_id in request.form.getlist('chefs'):
            dinner.chefs.append(User.query.get(int(user_id)))

        # Guests
        g = Counter(form.guests.data.splitlines())

        GuestAssociation.query.filter(
            GuestAssociation.dinner_id == dinner.id
        ).delete()

        if form.guests.data is None or str(form.guests.data).isspace() or str(form.guests.data) is "":
            db.session.commit()
            flash("It all went according to plan :-))))))", "alert alert-info")
            return redirect(url_for("dinner_club.meal", dinner_id=dinner.id))
        with db.session.no_autoflush:
            for key in g:
                if key.isspace():
                    break
                user = User.query.filter(
                    User.name == key
                ).first()
                if user:
                    numbers = g[key]
                    try:
                        ga = GuestAssociation(number_of_guests=numbers)
                        ga.user = user
                        dinner.guests.append(ga)
                        db.session.commit()
                    except DBAPIError as e:
                        print(str(e))
                        db.session.rollback()
                else:
                    flash("Couldn't find guest with name {0}. Are you sure it's correct?".format(key))
                    return redirect(url_for('dinner_club.edit', dinner_id=dinner_id))

    users = User.query.filter(
        User.subscribed_to_dinner_club,
        User.active
    ).all()

    return render_template("dinner_club/edit.html", users=users, dinner=dinner, form=form)
