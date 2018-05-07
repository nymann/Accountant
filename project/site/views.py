from flask import render_template, redirect, url_for, flash
from flask_login import login_user, login_required, logout_user
from project.models import User
from project.forms import LoginForm
from werkzeug.security import generate_password_hash, check_password_hash
from . import site


@site.route('/')
def index():
    return "hello"


@site.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if not user:
            flash("Brugernavn eksisterer ikke eller kodeordet er forkert", "alert alert-danger")
            return redirect(url_for('site.login'))
        if check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            flash("Success", "alert alert-info")
            return redirect(url_for('site.index'))

    return render_template('site/login.html', form=form)


@site.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('site.index'))


@site.route('/signup')
def signup():
    pass
