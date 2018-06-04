from datetime import datetime

from flask import render_template, redirect, url_for, flash, request
from flask_login import current_user, login_required
from sqlalchemy import or_, func
from sqlalchemy.exc import DBAPIError
from sqlalchemy.sql import label

from project.forms import UserForm
from project.models import User, Dinner, MeetingEvent, Shopping, Items, db, MeetingTopic, OAuth, BeverageUser, Beverage, \
    BeverageBatch, BeverageID, BeverageTypes
from project.site import site
from project.utils.uploadsets import avatars, process_user_avatar


@site.route('/')
@login_required
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

    # topics
    topics = MeetingTopic.query.filter(
        MeetingTopic.talked_about.is_(False)
    ).all()

    # most recent purchase
    purchase = Shopping.query.filter(
        Shopping.accounted.is_(False)
    ).order_by(
        Shopping.date.desc()
    ).first()

    return render_template('site/index.html', latest_dinner=latest_dinner, event=event, topics=topics,
                           purchase=purchase)


@site.route('/login')
def login():
    return render_template('site/login.html')


@site.route('/profile/<int:user_id>', methods=['GET', 'POST'])
@login_required
def profile(user_id):
    user = User.query.get_or_404(user_id)
    oauths = OAuth.query.filter(
        OAuth.user_id == user_id
    ).all()

    shopping_list_entries = Shopping.query.filter(
        Shopping.accounted.is_(False),
        Shopping.payee_id.is_(user_id)
    ).all()

    non_accounted_shopping_entries = Shopping.query.filter(
        Shopping.accounted.is_(False)
    ).all()

    shopping_expenses = 0.0
    if user.active:
        for shopping in non_accounted_shopping_entries:
            active_members = db.session.query(
                func.count(User.id)
            ).filter(
                User.active,
                or_(User.move_in_date.is_(None), User.move_in_date <= shopping.date)
            ).scalar()
            for item in shopping.items:
                if (user.move_in_date is None or user.move_in_date <= shopping.date) and (
                        user.move_out_date is None or user.move_in_date >= shopping.date):
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
    if user.active:
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

    beverage_expenses = db.session.query(
        func.sum(BeverageBatch.price_per_can)
    ).join(
        BeverageUser
    ).filter(
        BeverageBatch.beverage_id == BeverageUser.beverage_batch_id,
        BeverageUser.user_id == user.id
    ).scalar()
    beverage_expenses = beverage_expenses if beverage_expenses else 0.0

    beverage_income = db.session.query(
        func.sum(BeverageBatch.total_price)
    ).filter(
        BeverageBatch.payee_id == user.id
    ).scalar()
    beverage_income = beverage_income if beverage_income else 0.0

    beverages_bought = db.session.query(
        label("price", func.count(Beverage.id) * BeverageBatch.price_per_can),
        BeverageTypes.type.label("type"),
        Beverage.name.label("name"),
        label("count", func.count(Beverage.id))
    ).join(
        BeverageUser
    ).join(
        Beverage
    ).join(
        BeverageTypes
    ).group_by(
        Beverage.name
    ).filter(
        BeverageBatch.accounted.is_(False),
        BeverageUser.user_id == user.id
    ).all()
    total_income = beverage_income + dinner_income + shopping_income
    total_expenses = beverage_expenses + dinner_expenses + shopping_expenses
    total_balance = total_income - total_expenses
    form = UserForm()
    if form.validate_on_submit() and (current_user.id is user.id or current_user.admin):
        old_avatar_url = user.picture_url
        filename = None
        try:
            user.email = form.email.data
            user.name = form.name.data
            user.subscribed_to_dinner_club = form.subscribed_to_dinner_club.data
            user.phone_number = form.phone_number.data
            user.move_in_date = datetime.strptime(form.move_in_date.data, "%d/%m/%Y")
            user.room_number = form.room_number.data
            if 'picture' in request.files:
                filename = process_user_avatar(request.files['picture'], avatars)
                user.picture_url = filename

            if current_user.admin:
                user.admin = form.admin.data
                user.active = form.active.data
                move_out_date = str(form.move_out_date)
                if move_out_date and move_out_date.isspace():
                    user.move_out_date = datetime.strptime(move_out_date, "%d/%m/%Y")

            db.session.commit()
            if filename and old_avatar_url:
                #     TODO DELETE PIC
                print("delete")
            flash("Updated", "alert alert-info")
            return redirect(url_for('site.profile', user_id=user_id))

        except DBAPIError as e:
            flash(str(e), "alert alert-danger")

    return render_template('site/profile.html', user=user, form=form, shopping_list_entries=shopping_list_entries,
                           shopping_income=shopping_income, shopping_expenses=shopping_expenses,
                           dinner_income=dinner_income, dinner_expenses=dinner_expenses, oauths=oauths,
                           beverage_expenses=beverage_expenses, beverage_income=beverage_income,
                           beverages_bought=beverages_bought, total_balance=total_balance, total_income=total_income,
                           total_expenses=total_expenses)


@site.route('/residents')
@login_required
def residents():
    active_residents = User.query.filter(
        User.active
    ).all()

    inactive_residents = User.query.filter(
        or_(User.active.is_(None), User.active.is_(False))
    ).all()

    return render_template('site/residents.html', active_residents=active_residents,
                           inactive_residents=inactive_residents)


@site.route('/private_policy')
def private_policy():
    return render_template('site/private_policy.html')
