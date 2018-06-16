from collections import Counter

from dateutil.relativedelta import relativedelta
from datetime import time
from flask import render_template, request, abort
from flask_login import login_required
from sqlalchemy.exc import DBAPIError
from sqlalchemy.sql import label

import project
from project.dinner_club import dinner_club
from project.forms import DinnerForm, ParticipateForm
from project.models import GuestAssociation
from project.utils.decorators import *
from project.utils.helper import *


@dinner_club.route('/new', methods=['GET', 'POST'])
@active
def new():
    # active_dinner_club_participants
    users = User.query.filter(
        User.subscribed_to_dinner_club,
        User.active
    ).order_by(User.name).all()

    form = DinnerForm(participants=users)
    if form.validate_on_submit():
        payee_id = form.payee.data if form.payee.data and current_user.admin else current_user.id
        dish_name = form.dish_name.data
        # value checker
        if len(form.price.data) > 0:
            try:
                price = float(form.price.data)
            except ValueError as e:
                flash(str(e), 'alert alert-danger')
                return redirect(url_for('dinner_club.new'))
        else:
            price = None

        start = datetime.strptime("%s %s" % (form.date.data, form.time.data), "%d/%m/%Y %H:%M")

        participants = list()
        for user_id in request.form.getlist('participants'):
            participants.append(User.query.get(int(user_id)))

        chefs = list()
        for user_id in request.form.getlist('chefs'):
            chefs.append(User.query.get(int(user_id)))

        d = Dinner(payee_id=payee_id, price=price, datetime=start, participants=participants, chefs=chefs,
                   dish_name=dish_name)

        try:
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
@login_required
def index():
    form = ParticipateForm()
    # Getting the current date.
    curDate = datetime.now()

    # Latest dinner
    latest_dinner = Dinner.query.filter(
        Dinner.accounted.is_(False),
        Dinner.datetime < curDate
    ).order_by(
        Dinner.datetime.desc()
    ).first()

    time_limit = datetime.now() + relativedelta(hours=36)
    # Future dinners
    dinners_future = db.session.query(
        Dinner.id.label('id'),
        Dinner.datetime.label('datetime'),
        User.name.label('payee'),
        Dinner.dish_name.label('dish_name'),
        label("can_participate", Dinner.datetime >= time_limit)
    ).join(
        User
    ).filter(
        Dinner.accounted.is_(False),
        Dinner.datetime >= curDate
    ).order_by(
        Dinner.datetime.desc()
    ).all()

    # Past dinners
    dinners_past = Dinner.query.filter(
        Dinner.accounted.is_(False),
        Dinner.datetime < curDate
    ).order_by(
        Dinner.datetime.desc()
    ).all()

    # dinners_future = Dinner.query.filter(
    #     Dinner.accounted.is_(False),
    #     Dinner.datetime >= curDate
    # ).order_by(
    #     Dinner.datetime.desc()
    # ).all()

    return render_template('dinner_club/index.html', dinners_future=dinners_future, dinners_past=dinners_past,
                           latest_dinner=latest_dinner, form=form)


@dinner_club.route('/meal/<dinner_id>')
@login_required
def meal(dinner_id):
    dinner = Dinner.query.get_or_404(int(dinner_id))
    return render_template('dinner_club/meal.html', dinner=dinner)


@dinner_club.route('/meal/edit/<dinner_id>', methods=['GET', 'POST'])
@login_required
def edit(dinner_id):
    form = DinnerForm()
    dinner = Dinner.query.get(int(dinner_id))
    if dinner.payee_id is not current_user.id and not is_admin():
        return abort(403)
    if form.validate_on_submit():
        try:
            price = float(form.price.data)
        except ValueError as e:
            flash(str(e), 'alert alert-danger')
            return redirect(url_for('dinner_club.new'))
        dinner.price = price
        dinner.dish_name = form.dish_name.data
        Dinner.datetime = datetime.strptime(form.date.data, "%d/%m/%Y")
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
                        project.sentry.captureMessage(str(e))
                        db.session.rollback()
                else:
                    flash("Couldn't find guest with name {0}. Are you sure it's correct?".format(key))
                    return redirect(url_for('dinner_club.edit', dinner_id=dinner_id))

    users = User.query.filter(
        User.subscribed_to_dinner_club,
        User.active
    ).all()

    return render_template("dinner_club/edit.html", users=users, dinner=dinner, form=form)


@dinner_club.route('/meal/delete/<dinner_id>')
def delete(dinner_id):
    dinner = Dinner.query.get_or_404(int(dinner_id))
    if not current_user.admin and current_user.id is not dinner.payee_id:
        flash("You can't delete the event because you didn't pay and you are not admin.", "alert alert-danger")
        return redirect(url_for('dinner_club.meal', dinner_id=dinner_id))
    try:
        GuestAssociation.query.filter(
            GuestAssociation.dinner_id == dinner_id
        ).delete()
        db.session.delete(dinner)
        db.session.commit()
        flash("Deletion successful", "alert alert-info ")
    except DBAPIError as e:
        db.session.rollback()
        project.sentry.captureMessage(str(e))
        flash(str(e), "alert alert-danger")
        return redirect(url_for('dinner_club.meal', dinner_id=dinner_id))
    return redirect(url_for('dinner_club.index'))


@dinner_club.route('/participate/<int:user_id>/<int:dinner_id>', methods=['GET', 'POST'])
def participate(user_id, dinner_id):
    dinner = Dinner.query.get_or_404(dinner_id)

    # if dinner.datetime < datetime.now() + relativedelta(hours=36):
    #     return abort(502)
    if dinner.date.datetime() < (datetime.now() + relativedelta(day=1)) and datetime.now().time().hour > 7:
        return abort(502)

    if current_user in dinner.participants:
        dinner = Dinner.query.get(int(dinner_id))
        dinner.participants.remove(User.query.get(int(user_id)))
        msg = "You are successfully removed from the dinner!"
    else:
        dinner = Dinner.query.get(int(dinner_id))
        dinner.participants.append(User.query.get(int(user_id)))
        msg = "You are successfully added to the dinner!"

    try:
        db.session.commit()
        flash(msg, "alert alert-info")
    except DBAPIError as e:
        db.session.rollback()
        project.sentry.captureMessage(str(e))
        flash(str(e), "alert alert-danger")

    return index()
