import logging

from flask import Flask
from flask_login import LoginManager
from flask_mail import Mail
from flask_mobility import Mobility
from flask_uploads import configure_uploads
from raven.contrib.flask import Sentry
from werkzeug.contrib.fixers import ProxyFix

from config import DevelopmentConfig
from project.apis import api_blueprint as api
from project.utils.error_handlers import register_handlers
from project.utils.uploadsets import avatars

mobility = Mobility()
mail = Mail()
sentry = Sentry()

login_manager = LoginManager()
login_manager.login_view = '/login'
login_manager.login_message = 'You have to login in order to view that page.'
login_manager.login_message_category = 'alert alert-danger'


def format_datetime(value):
    return value.strftime("%d/%m/%Y")


def create_app(cfg=DevelopmentConfig):
    app = Flask(__name__)
    app.jinja_env.filters['datetime'] = format_datetime
    app.config.from_object(cfg)
    app.wsgi_app = ProxyFix(app.wsgi_app)

    register_extensions(app=app)
    register_blueprints(app=app)
    register_handlers(app=app)
    return app


def register_extensions(app):
    from project.models import db, User
    db.init_app(app)
    with app.app_context():
        db.create_all(app=app)

    # Login manager
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Flask uploads
    configure_uploads(app, avatars)

    # Sentry
    sentry.init_app(app=app, logging=True, level=logging.ERROR)

    # Mobility
    mobility.init_app(app=app)

    # Flask Mail
    mail.init_app(app=app)


def register_blueprints(app):
    # Site blueprints
    from project.beverage_club import beverage_club
    from project.dinner_club import dinner_club
    from project.feedback import feedback
    from project.kitchen_meeting import kitchen_meeting
    from project.models import db, User, OAuth
    from project.shopping_list import shopping_list
    from project.site import site
    from project.utils.social_blueprints import facebook_blueprint, twitter_blueprint, github_blueprint

    app.register_blueprint(facebook_blueprint, url_prefix='/login')
    app.register_blueprint(twitter_blueprint, url_prefix='/login')
    app.register_blueprint(github_blueprint, url_prefix='/login')
    app.register_blueprint(site, url_prefix='')
    app.register_blueprint(beverage_club, url_prefix='/beverage_club')
    app.register_blueprint(dinner_club, url_prefix='/dinner_club')
    app.register_blueprint(feedback, url_prefix='/feedback')
    app.register_blueprint(kitchen_meeting, url_prefix='/kitchen_meeting')
    app.register_blueprint(shopping_list, url_prefix='/shopping_list')
    app.register_blueprint(api, url_prefix='/api')
