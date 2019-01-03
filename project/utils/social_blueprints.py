from flask_dance.consumer import oauth_authorized, oauth_error
from flask_dance.consumer.backend.sqla import SQLAlchemyBackend
from flask_dance.contrib.facebook import make_facebook_blueprint
from flask_dance.contrib.github import make_github_blueprint
from flask_dance.contrib.twitter import make_twitter_blueprint
from flask_login import current_user

from project.utils.login import general_logged_in, general_error

from project.models import OAuth, db

facebook_blueprint = make_facebook_blueprint(
    backend=SQLAlchemyBackend(OAuth, db.session, user=current_user, user_required=False)
)

twitter_blueprint = make_twitter_blueprint(
    backend=SQLAlchemyBackend(OAuth, db.session, user=current_user, user_required=False)
)

github_blueprint = make_github_blueprint(
    backend=SQLAlchemyBackend(OAuth, db.session, user=current_user, user_required=False)
)


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
