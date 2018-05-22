from flask import Flask, flash, redirect, url_for
from flask_dance.consumer import oauth_authorized
from flask_dance.consumer.backend.sqla import SQLAlchemyBackend
from flask_dance.contrib.facebook import make_facebook_blueprint
from flask_login import LoginManager, login_user, current_user, login_required, logout_user
from flask_uploads import configure_uploads
from sqlalchemy.orm.exc import NoResultFound

from project.api import api
from project.dinner_club import dinner_club
from project.kitchen_meeting import kitchen_meeting
from project.models import db, User, OAuth
from project.shopping_list import shopping_list
from project.site import site
from project.utils.uploadsets import avatars

import os
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

app = Flask(__name__)

app.config.from_pyfile('../config.cfg', silent=False)

facebook_blueprint = make_facebook_blueprint(
    backend=SQLAlchemyBackend(OAuth, db.session, user=current_user)
)

app.register_blueprint(facebook_blueprint, url_prefix='/login')
app.register_blueprint(site, url_prefix='')
app.register_blueprint(api, url_prefix='/api')
app.register_blueprint(dinner_club, url_prefix='/dinner_club')
app.register_blueprint(kitchen_meeting, url_prefix='/kitchen_meeting')
app.register_blueprint(shopping_list, url_prefix='/shopping_list')

configure_uploads(app, avatars)
login_manager = LoginManager(app)
db.app = app
db.init_app(app)
db.create_all()


@oauth_authorized.connect_via(facebook_blueprint)
def facebook_logged_in(blueprint, token):
    # http://flask-dance.readthedocs.io/en/latest/multi-user.html
    if not token:
        flash("Failed to log in with Facebook.", "alert alert-danger")
        return False

    resp = blueprint.session.get('/me?fields=id,name')
    if not resp.ok:
        flash("Failed to get user from Facebook", "alert alert-danger")
        return False
    facebook_info = resp.json()
    print("This is what we got '{0}'".format(facebook_info))
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
        flash("Successfully signed in via Facebook", "alert alert-info")
    else:
        mail = facebook_info['email'] if 'email' in facebook_info else None
        user = User(
            email=mail,
            name=facebook_info['name']
        )

        oauth.user = user
        db.session.add_all([user, oauth])
        db.session.commit()
        login_user(user)
        flash("Successfully signed in via Facebook", "alert alert-info")

    return False


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
