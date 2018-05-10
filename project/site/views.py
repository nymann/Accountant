from flask import render_template, redirect, url_for, flash
from flask_login import login_user, login_required, logout_user, current_user
from project.models import User
from project.forms import LoginForm, RegisterForm, UserForm
from werkzeug.security import generate_password_hash, check_password_hash
from project.site import site
from project.models import db
from sqlalchemy.exc import DBAPIError


@site.route('/')
def index():
    return render_template('site/base.html')


@site.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter(User.email == form.email.data).first()
        if not user:
            flash("User doesn't exist.", "alert alert-danger")
            return redirect(url_for('site.login'))
        if check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            flash("Success", "alert alert-info")
            return redirect(url_for('site.index'))
        flash("Email or Password is wrong.", "alert alert-danger")
        return redirect(url_for('site.login'))

    return render_template('site/login.html', form=form)


@site.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('site.index'))


@site.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method='sha256')
        # noinspection PyArgumentList
        new_user = User(email=form.email.data, password=hashed_password)
        try:
            db.session.add(new_user)
            db.session.commit()
            flash("{0} created successfully.".format(new_user.email), "alert alert-info")
            login_user(new_user)
            return redirect(url_for('site.index'))
        except DBAPIError as e:
            db.session.rollback()
            flash(str(e), "alert alert-danger")
            return redirect(url_for('site.register'))
    return render_template('site/register.html', form=form)


@site.route('/profile/<user_id>', methods=['GET', 'POST'])
def profile(user_id):
    user = User.query.get(user_id)
    form = UserForm()

    if form.validate_on_submit():
        user.email = form.email.data
        user.name = form.name.data
        user.subscribed_to_dinner_club = form.subscribed_to_dinner_club.data
        if current_user.admin:
            user.admin = form.admin.data

        try:
            db.session.commit()
            flash("Updated", "alert alert-info")
            return redirect(url_for('site.profile', user_id=user_id))
        except DBAPIError as e:
            flash(str(e), "alert alert-danger")

    return render_template('site/profile.html', user=user, form=form)
