from datetime import datetime

from flask import render_template, redirect, url_for, flash, request, abort, send_from_directory
from flask_login import current_user, login_required
from sqlalchemy import or_, func, desc, asc
from sqlalchemy.exc import DBAPIError
from sqlalchemy.sql import label
from sqlalchemy.sql.operators import is_

from project.forms import UserForm
from project.models import (
    User, Dinner, MeetingEvent, Shopping, db, MeetingTopic, OAuth, BeverageUser, Beverage, BeverageBatch,
    BeverageTypes, UserReport, AccountingReport)
from project.site import site
from project.utils.helper import UserHelper, generate_calendar
from project.utils.uploadsets import avatars, process_user_avatar


@site.route('/')
@login_required
def index():
    # next meal
    try:
        next_dinner = Dinner.query.filter(
            Dinner.datetime >= datetime.now()
        ).order_by(
            asc(Dinner.datetime)
        ).first()
    except DBAPIError as e:
        flash(str(e), "alert alert-danger")

    # next meeting
    try:
        event = MeetingEvent.query.filter(
            MeetingEvent.completed.is_(False)
        ).order_by(
            desc(MeetingEvent.id)
        ).first()
    except DBAPIError as e:
        flash(str(e), "alert alert-danger")

    # topics
    topics = MeetingTopic.query.filter(
        MeetingTopic.talked_about.is_(False)
    ).all()

    # most recent purchase
    try:
        purchase = Shopping.query.filter(
            Shopping.accounting_id.is_(None)
        ).order_by(
            desc(Shopping.date)
        ).first()
    except DBAPIError as e:
        flash(str(e), "alert alert-danger")

    report = AccountingReport.query.order_by(AccountingReport.date.desc()).first()

    return render_template('site/index.html', next_dinner=next_dinner, event=event, topics=topics,
                           purchase=purchase, report=report)


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
        Shopping.accounting_id.is_(None),
        Shopping.payee_id.is_(user_id)
    ).order_by(Shopping.date).all()

    beverages_bought = db.session.query(
        label("price", func.count(Beverage.id) * BeverageBatch.price_per_can),
        BeverageTypes.type.label("type"),
        Beverage.name.label("name"),
        label("count", func.count(Beverage.id))
    ).join(BeverageUser).join(Beverage).join(BeverageTypes).group_by(Beverage.name).filter(
        BeverageUser.accounting_id.is_(None),
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
                move_out_date = str(form.move_out_date.data).strip()
                if move_out_date:
                    user.move_out_date = datetime.strptime(move_out_date, "%d/%m/%Y")

            db.session.commit()
            # if filename and old_avatar_url:
            #     #     TODO DELETE PIC

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
    reports = AccountingReport.query.order_by(desc(AccountingReport.date)).all()
    return render_template('site/reports.html', reports=reports)


@site.route('/report/<int:report_id>')
@login_required
def report(report_id):
    accounting_report = AccountingReport.query.get(report_id)
    if not accounting_report:
        return abort(404)

    # Beverages consumed pr. inhabitant.
    beverage_stats = db.session.query(
        label("consumed", func.count(BeverageUser.user_id)),
        label("user_name", User.name),
        label("user_id", User.id)
    ).join(User).filter(
        BeverageUser.accounting_id.is_(report_id)
    ).group_by(BeverageUser.user_id).order_by(desc("consumed")).all()

    # Times paid for dinner_club
    dinners_paid = db.session.query(
        label("paid", func.count(Dinner.payee_id)),
        label("user_name", User.name),
        label("user_id", User.id)
    ).join(User).filter(
        Dinner.accounting_id.is_(report_id),
    ).group_by(Dinner.payee_id).order_by(desc("paid")).all()

    return render_template(
        'site/report.html', report=accounting_report, beverage_stats=beverage_stats, dinners_paid=dinners_paid
    )


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
            user_id=u.user.id, dinner_balance=u.dinner_balance(), shopping_balance=u.shopping_balance(),
            beverage_balance=u.beverage_balance(), total_balance=u.total_balance()
        )
        try:
            accounting_report.user_reports.append(report)
            db.session.commit()
        except DBAPIError as e:
            db.session.rollback()
            flash(str(e), "alert alert-danger")

    beverages_bought = BeverageUser.query.filter(BeverageUser.accounting_id.is_(None)).all()

    # Beverage
    for beverage in beverages_bought:
        beverage.accounting_id = accounting_report.id
        db.session.commit()

    # Dinner
    dinners = Dinner.query.filter(
        Dinner.accounting_id.is_(None),
        Dinner.datetime < datetime.now()
    ).all()
    for dinner in dinners:
        dinner.accounting_id = accounting_report.id
        db.session.commit()

    # Shopping
    shoppings = Shopping.query.filter(Shopping.accounting_id.is_(None)).all()
    for shopping in shoppings:
        shopping.accounting_id = accounting_report.id
        db.session.commit()

    return redirect(url_for('site.reports'))


@site.route('/developer')
@login_required
def developer():
    username = current_user.name
    userid = current_user.id

    oauthtoken = OAuth.query.filter(
        OAuth.user_id == userid
    ).first().token

    apitoken = None

    if not apitoken:
        try:
            apitoken = oauthtoken['access_token']
        except KeyError as e:
            print(str(e))
    if not apitoken:
        try:
            apitoken = oauthtoken['oauth_token_secret']
        except KeyError as e:
            print(str(e))

    return render_template('site/developer.html', username=username, apitoken=apitoken)


@site.route('/change_paid_status/<int:report_id>/<int:user_id>')
def change_paid_status(report_id, user_id):
    if not current_user.admin:
        return abort(403)
    report = UserReport.query.filter(
        UserReport.accounting_report_id == report_id,
        UserReport.user_id == user_id
    ).one()
    report.paid = not report.paid
    db.session.commit()
    return redirect(url_for('site.report', report_id=report_id))


@site.route('/dinner_history/<int:report_id>/<int:user_id>')
def dinner_history(report_id, user_id):
    user = User.query.get(user_id)
    report = AccountingReport.query.get(report_id)
    dinners = Dinner.query.filter(Dinner.accounting_id == report_id)
    user_helper = UserHelper(user)
    return render_template(
        'site/dinner_history.html', user=user, report=report, dinners=dinners, user_helper=user_helper
    )


@site.route('/shopping_history/<int:report_id>/<int:user_id>')
def shopping_history(report_id, user_id):
    user = User.query.get(user_id)
    user_helper = UserHelper(user)
    report = AccountingReport.query.get(report_id)
    move_out_date = user.move_out_date if user.move_out_date else datetime.strptime('01-01-3000', '%d-%m-%Y')
    move_in_date = user.move_in_date if user.move_in_date else datetime.strptime('01-01-2000', '%d-%m-%Y')
    shopping_entries = Shopping.query.filter(
        Shopping.accounting_id == report_id,
        move_out_date >= Shopping.date,
        move_in_date <= Shopping.date
    ).order_by(
        Shopping.date.asc()
    ).all()

    return render_template(
        'site/shopping_history.html', user=user, report=report, shopping_entries=shopping_entries,
        user_helper=user_helper
    )


@site.route('/calendar')
def calender():
    generate_calendar()

    # return url_for('static/calendar', filename='calendar.ics')
    return send_from_directory('static/calendar', filename='calendar.ics')