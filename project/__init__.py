from flask import Flask, flash, redirect, url_for
from flask_dance.consumer import oauth_authorized
from flask_dance.consumer.backend.sqla import SQLAlchemyBackend
from flask_dance.contrib.facebook import make_facebook_blueprint
from flask_dance.contrib.twitter import make_twitter_blueprint
from flask_dance.contrib.github import make_github_blueprint
from flask_login import LoginManager, login_user, current_user, login_required, logout_user
from flask_uploads import configure_uploads
from sqlalchemy import or_
from sqlalchemy.orm.exc import NoResultFound

from project.api import api
from project.beverage_club import beverage_club
from project.dinner_club import dinner_club
from project.kitchen_meeting import kitchen_meeting
from project.models import db, User, OAuth
from project.shopping_list import shopping_list
from project.site import site
from project.utils.uploadsets import avatars
from project.utils.login import general_logged_in

import os

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

app = Flask(__name__)

app.config.from_pyfile('../config.cfg', silent=False)

facebook_blueprint = make_facebook_blueprint(
    backend=SQLAlchemyBackend(OAuth, db.session, user=current_user)
)

twitter_blueprint = make_twitter_blueprint(
    backend=SQLAlchemyBackend(OAuth, db.session, user=current_user, user_required=False)
)

github_blueprint = make_github_blueprint(
    backend=SQLAlchemyBackend(OAuth, db.session, user=current_user)
)

app.register_blueprint(facebook_blueprint, url_prefix='/login')
app.register_blueprint(twitter_blueprint, url_prefix='/login')
app.register_blueprint(github_blueprint, url_prefix='/login')
app.register_blueprint(site, url_prefix='')
app.register_blueprint(api, url_prefix='/api')
app.register_blueprint(beverage_club, url_prefix='/beverage_club')
app.register_blueprint(dinner_club, url_prefix='/dinner_club')
app.register_blueprint(kitchen_meeting, url_prefix='/kitchen_meeting')
app.register_blueprint(shopping_list, url_prefix='/shopping_list')

configure_uploads(app, avatars)


@oauth_authorized.connect_via(twitter_blueprint)
def twitter_logged_in(blueprint, token):
    if not token:
        flash("Failed to log in with Twitter.", "alert alert-danger")
        return False

    resp = blueprint.session.get('account/settings.json')
    if not resp.ok:
        print(str(resp.json()))
        flash("Failed to get user from Twitter", "alert alert-danger")
        return False
    twitter_info = resp.json()
    twitter_user_id = twitter_info['screen_name']
    id = hash(twitter_user_id)
    twitter_user_id = int(id)
    query = OAuth.query.filter_by(
        provider=blueprint.name,
        provider_user_id=twitter_user_id
    )
    try:
        oauth = query.one()

    except NoResultFound:
        oauth = OAuth(
            provider=blueprint.name,
            token=token,
            provider_user_id=twitter_user_id
        )

    if oauth and oauth.user:
        login_user(oauth.user)
        flash("Successfully signed in via Twitter", "alert alert-info")
    else:
        mail = twitter_info['email'] if 'email' in twitter_info else None
        user = User(
            email=mail,
            name=twitter_info['screen_name']
        )

        oauth.user = user
        db.session.add_all([user, oauth])
        db.session.commit()
        login_user(user)
        flash("Successfully signed in via Twitter", "alert alert-info")
    return False


@oauth_authorized.connect_via(facebook_blueprint)
def facebook_logged_in(blueprint, token):
    # http://flask-dance.readthedocs.io/en/latest/multi-user.html
    if not token:
        flash("Failed to log in with Facebook.", "alert alert-danger")
        return False

    resp = blueprint.session.get('/me?fields=id,name,email')
    if not resp.ok:
        flash("Failed to get user from Facebook", "alert alert-danger")
        return False
    facebook_info = resp.json()
    facebook_user_id = facebook_info['id']
    query = OAuth.query.filter_by(
        provider=blueprint.name,
        provider_user_id=facebook_user_id
    )
    try:
        oauth = query.one()

    except NoResultFound:
        oauth = OAuth(
            provider=blueprint.name,
            token=token,
            provider_user_id=facebook_user_id
        )

    if oauth.user:
        login_user(oauth.user)
        flash("Successfully signed in via %s" % blueprint.name, "alert alert-info")
    else:
        mail = facebook_info['email'] if 'email' in facebook_info else None
        name = facebook_info['name']
        if current_user.is_authenticated:
            user = User.query.get(current_user.id)
        else:
            user = User.query.filter(
                or_(User.email == mail, User.name == name)
            ).one_or_none()
            if not user:
                user = User(
                    email=mail,
                    name=name
                )

        oauth.user = user
        db.session.add_all([user, oauth])
        db.session.commit()
        login_user(user)
        flash("Successfully signed in via Facebook", "alert alert-info")

    return False


@oauth_authorized.connect_via(github_blueprint)
def github_logged_in(blueprint, token):
    # http://flask-dance.readthedocs.io/en/latest/multi-user.html
    if not token:
        flash("Failed to log in with %s." % blueprint.name, "alert alert-danger")
        return False

    resp = blueprint.session.get('/user')
    if not resp.ok:
        flash("Failed to get user from %s" % blueprint.name, "alert alert-danger")
        return False
    github_info = resp.json()
    github_user_id = github_info['id']
    query = OAuth.query.filter_by(
        provider=blueprint.name,
        provider_user_id=github_user_id
    )
    try:
        oauth = query.one()

    except NoResultFound:
        oauth = OAuth(
            provider=blueprint.name,
            token=token,
            provider_user_id=github_user_id
        )

    if oauth.user:
        login_user(oauth.user)
        flash("Successfully signed in via %s" % blueprint.name, "alert alert-info")
    else:
        mail = github_info['email'] if 'email' in github_info else None
        name = github_info['name']
        if current_user.is_authenticated:
            user = User.query.get(current_user.id)
        else:
            user = User.query.filter(
                or_(User.email == mail, User.name == name)
            ).one_or_none()
            if not user:
                user = User(
                    email=mail,
                    name=name
                )

        oauth.user = user
        db.session.add_all([user, oauth])
        db.session.commit()
        login_user(user)
        flash("Successfully signed in via %s" % blueprint.name, "alert alert-info")

    return False


login_manager = LoginManager(app)
db.app = app
db.init_app(app)
db.create_all()


def format_datetime(value):
    return value.strftime("%d/%m/%Y")


app.jinja_env.filters['datetime'] = format_datetime


@app.after_request
def add_header(response):
    response.cache_control.private = True
    response.cache_control.public = False
    return response


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('site.index'))
