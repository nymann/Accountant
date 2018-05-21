from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, login_required, logout_user, current_user
from sqlalchemy import or_, func
from sqlalchemy.sql import label
from sqlalchemy.exc import DBAPIError
from werkzeug.security import generate_password_hash, check_password_hash

from project.forms import LoginForm, RegisterForm, UserForm
from project.models import User, Dinner, MeetingEvent, Shopping, Items
from project.models import db
from project.site import site
from project.utils.uploadsets import avatars, process_user_avatar
from datetime import datetime


@site.route('/')
def index():
    # latest meal
    latest_dinner = Dinner.query.filter(
        Dinner.accounted.is_(False)
    ).order_by(
        Dinner.date.desc()
    ).first()

    # next meeting
    event = MeetingEvent.query.filter(
        MeetingEvent.completed.is_(False)
    ).order_by(
        MeetingEvent.id.desc()
    ).first()

    return render_template('site/index.html', latest_dinner=latest_dinner, event=event)


@site.route('/profile/<int:user_id>', methods=['GET', 'POST'])
def profile(user_id):
    user = User.query.get_or_404(user_id)

    shopping_list_entries = Shopping.query.filter(
        Shopping.accounted.is_(False),
        Shopping.payee_id.is_(user_id)
    ).all()

    active_members = db.session.query(
        func.count(User.id)
    ).filter(
        User.active
    ).scalar()

    non_accounted_shopping_entries = Shopping.query.filter(
        Shopping.accounted.is_(False)
    ).all()

    shopping_expenses = 0.0
    for shopping in non_accounted_shopping_entries:
        for item in shopping.items:
            shopping_expenses += (item.price * item.amount) / active_members

    shopping_income = db.session.query(
        func.sum(Items.price * Items.amount)
    ).join(Shopping).filter(
        Shopping.payee_id.is_(user_id),
        Shopping.accounted.is_(False)
    ).scalar()
    shopping_income = shopping_income if shopping_income else 0.0

    dinner_income = db.session.query(
        func.sum(Dinner.price)
    ).filter(
        Dinner.payee_id.is_(user_id),
        Dinner.accounted.is_(False)
    ).scalar()
    dinner_income = dinner_income if dinner_income else 0.0

    non_accounted_dinners = Dinner.query.filter(
        Dinner.accounted.is_(False)
    ).all()
    dinner_expenses = 0.0
    for dinner in non_accounted_dinners:
        if user not in dinner.participants:
            continue
        # How many participated?
        number_of_guests = 0
        for guest in dinner.guests:
            number_of_guests += guest.number_of_guests
        number_of_participants = len(dinner.participants) + number_of_guests
        dinner_expenses += dinner.price / number_of_participants
        for guest in dinner.guests:
            if guest.user_id is user_id:
                # It's our guest.
                dinner_expenses += guest.number_of_guests * dinner.price / number_of_participants

    form = UserForm()
    if form.validate_on_submit():
        try:
            user.email = form.email.data
            user.name = form.name.data
            user.subscribed_to_dinner_club = form.subscribed_to_dinner_club.data
            user.phone_number = form.phone_number.data
            user.move_in_date = datetime.strptime(form.move_in_date.data, "%d/%m/%Y")
            if 'picture' in request.files:
                filename = process_user_avatar(request.files['picture'], avatars)
                user.picture_url = filename

            if current_user.admin:
                user.admin = form.admin.data
                user.room_number = form.room_number.data
                user.active = form.active.data
                move_out_date = str(form.move_out_date)
                if move_out_date and move_out_date.isspace():
                    user.move_out_date = datetime.strptime(move_out_date, "%d/%m/%Y")

            db.session.commit()
            flash("Updated", "alert alert-info")
            return redirect(url_for('site.profile', user_id=user_id))

        except DBAPIError as e:
            flash(str(e), "alert alert-danger")

    return render_template('site/profile.html', user=user, form=form, shopping_list_entries=shopping_list_entries,
                           shopping_income=shopping_income, shopping_expenses=shopping_expenses,
                           dinner_income=dinner_income, dinner_expenses=dinner_expenses)


@site.route('/residents')
def residents():
    active_residents = User.query.filter(
        User.active
    ).all()

    inactive_residents = User.query.filter(
        or_(User.active.is_(None), User.active.is_(False))
    ).all()

    return render_template('site/residents.html', active_residents=active_residents,
                           inactive_residents=inactive_residents)
