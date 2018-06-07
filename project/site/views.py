from datetime import datetime

from flask import render_template, redirect, url_for, flash, request, abort
from flask_login import current_user, login_required
from sqlalchemy import or_, func, desc
from sqlalchemy.exc import DBAPIError
from sqlalchemy.sql import label

from project.forms import UserForm
from project.models import (
    User, Dinner, MeetingEvent, Shopping, Items, db, MeetingTopic, OAuth, BeverageUser, Beverage, BeverageBatch,
    BeverageTypes, UserReport, AccountingReport
)
from project.site import site
from project.utils.helper import UserHelper
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
    user_helper = UserHelper(user)
    oauths = OAuth.query.filter(
        OAuth.user_id == user_id
    ).all()

    shopping_list_entries = Shopping.query.filter(
        Shopping.accounted.is_(False),
        Shopping.payee_id.is_(user_id)
    ).all()

    beverages_bought = db.session.query(
        label("price", func.count(Beverage.id) * BeverageBatch.price_per_can),
        BeverageTypes.type.label("type"),
        Beverage.name.label("name"),
        label("count", func.count(Beverage.id))
    ).join(BeverageUser).join(Beverage).join(BeverageTypes).group_by(Beverage.name).filter(
        BeverageBatch.accounted.is_(False),
        BeverageUser.user_id == user.id
    ).all()

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
                           oauths=oauths, beverages_bought=beverages_bought, user_helper=user_helper)


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


@site.route('/reports')
@login_required
def reports():
    latest_report = AccountingReport.query.order_by(desc(AccountingReport.date)).first()
    older_reports = AccountingReport.query.order_by(desc(AccountingReport.date)).offset(1).all()
    return render_template('site/reports.html', report=latest_report, older_reports=older_reports)


@site.route('/reports/do_accounting')
@login_required
def do_accounting():
    if not current_user.admin:
        return abort(403)
    users = User.query.filter(
        User.active.is_(True)
    ).all()
    accounted_date = datetime.now()
    accounting_report = AccountingReport(date=accounted_date)
    db.session.add(accounting_report)
    for user in users:
        u = UserHelper(user)
        report = UserReport(
            user_id=u.user.id, dinner_balance=u.dinner_balance(), shopping_balance=u.dinner_balance(),
            beverage_balance=u.beverage_balance(), total_balance=u.total_balance()
        )
        try:
            accounting_report.user_reports.append(report)
            db.session.commit()
        except DBAPIError as e:
            flash(str(e), "alert alert-danger")

    beverageBatches = BeverageBatch.query.filter(BeverageBatch.accounted.is_(False)).all()
    for beverageBatch in beverageBatches:
        beverageBatch.accounted = True
        db.session.commit()
    dinners = Dinner.query.filter(Dinner.accounted.is_(False)).all()
    for dinner in dinners:
        dinner.accounted = True
        db.session.commit()
    shoppings = Shopping.query.filter(Shopping.accounted.is_(False)).all()
    for shopping in shoppings:
        shopping.accounted = True
        db.session.commit()

    return redirect(url_for('site.reports'))
