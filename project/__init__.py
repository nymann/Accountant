from flask import Flask, redirect, url_for, render_template
from flask_dance.consumer import oauth_authorized, oauth_error
from flask_dance.consumer.backend.sqla import SQLAlchemyBackend
from flask_dance.contrib.facebook import make_facebook_blueprint
from flask_dance.contrib.github import make_github_blueprint
from flask_dance.contrib.twitter import make_twitter_blueprint
from flask_login import LoginManager, current_user, login_required, logout_user
from flask_mail import Mail, Message
from flask_uploads import configure_uploads
from werkzeug.contrib.fixers import ProxyFix
from raven.contrib.flask import Sentry

# Site imports
from project.beverage_club import beverage_club
from project.dinner_club import dinner_club
from project.feedback import feedback
from project.kitchen_meeting import kitchen_meeting
from project.models import db, User, OAuth
from project.shopping_list import shopping_list
from project.site import site
# API import
from project.apis import api_blueprint as api

from project.utils.login import general_logged_in, general_error
from project.utils.uploadsets import avatars

# Flask Mobility
from flask_mobility import Mobility

import logging

app = Flask(__name__)
Mobility(app)
app.config.from_pyfile('../config.cfg', silent=False)
app.wsgi_app = ProxyFix(app.wsgi_app)
mail = Mail(app)


facebook_blueprint = make_facebook_blueprint(
    backend=SQLAlchemyBackend(OAuth, db.session, user=current_user, user_required=False)
)

twitter_blueprint = make_twitter_blueprint(
    backend=SQLAlchemyBackend(OAuth, db.session, user=current_user, user_required=False)
)

github_blueprint = make_github_blueprint(
    backend=SQLAlchemyBackend(OAuth, db.session, user=current_user, user_required=False)
)
# Site blueprints
app.register_blueprint(facebook_blueprint, url_prefix='/login')
app.register_blueprint(twitter_blueprint, url_prefix='/login')
app.register_blueprint(github_blueprint, url_prefix='/login')
app.register_blueprint(site, url_prefix='')
app.register_blueprint(beverage_club, url_prefix='/beverage_club')
app.register_blueprint(dinner_club, url_prefix='/dinner_club')
app.register_blueprint(feedback, url_prefix='/feedback')
app.register_blueprint(kitchen_meeting, url_prefix='/kitchen_meeting')
app.register_blueprint(shopping_list, url_prefix='/shopping_list')
# API blueprints
app.register_blueprint(api, url_prefix='/api')
# app.register_blueprint(api, subdomain='api')

sentry = Sentry(
    app, logging=True, level=logging.ERROR,
)

configure_uploads(app, avatars)
login_manager = LoginManager(app)
login_manager.login_view = '/login'
login_manager.login_message = 'You have to login in order to view that page.'
login_manager.login_message_category = 'alert alert-danger'
db.app = app


@app.errorhandler(403)
def forbidden(error):
    return render_template('403.html', msg=error)


@app.errorhandler(404)
def not_found(error):
    return render_template('404.html', msg=error)


@app.errorhandler(500)
def bad_request(error):
    return render_template('500.html', msg=error)


@app.errorhandler(502)
def bad_request(error):
    return render_template('502.html', msg=error)


@oauth_authorized.connect_via(twitter_blueprint)
def twitter_logged_in(blueprint, token):
    return general_logged_in(blueprint, token, 'account/settings.json')


@oauth_error.connect_via(twitter_blueprint)
def twitter_error(blueprint, error, error_description=None, error_uri=None):
    return general_error(blueprint, error, error_description, error_uri)


@oauth_authorized.connect_via(facebook_blueprint)
def facebook_logged_in(blueprint, token):
    return general_logged_in(blueprint, token, '/me?fields=id,name,email')


@oauth_error.connect_via(facebook_blueprint)
def facebook_error(blueprint, error, error_description=None, error_uri=None):
    return general_error(blueprint, error, error_description, error_uri)


@oauth_authorized.connect_via(github_blueprint)
def github_logged_in(blueprint, token):
    return general_logged_in(blueprint, token, '/user')


@oauth_error.connect_via(github_blueprint)
def github_error(blueprint, error, error_description=None, error_uri=None):
    return general_error(blueprint, error, error_description, error_uri)


db.init_app(app)
login_manager.init_app(app)
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
