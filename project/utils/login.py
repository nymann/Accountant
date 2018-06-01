import random
import string

from flask_login import current_user, login_user
from flask import flash
from sqlalchemy import or_
from sqlalchemy.orm.exc import NoResultFound

from project.models import User, OAuth, db


def general_logged_in(blueprint, token, get_string):
    # http://flask-dance.readthedocs.io/en/latest/multi-user.html
    if not token:
        flash("Failed to log in with %s." % blueprint.name, "alert alert-danger")
        return False

    resp = blueprint.session.get(get_string)
    if not resp.ok:
        return False
    info = resp.json()
    if 'id' in info:
        # facebook, GitHub
        user_id = int(info['id'])
    elif 'screen_name' in info:
        # twitter
        user_id = int(hash(info['screen_name']))
    else:
        flash("Failed to get id of user.", "alert alert-info")
        return False
    query = OAuth.query.filter_by(
        provider=blueprint.name,
        provider_user_id=user_id
    )
    try:
        oauth = query.one()
    except NoResultFound:
        oauth = OAuth(
            provider=blueprint.name,
            token=token,
            provider_user_id=user_id
        )

    if oauth.user:
        login_user(oauth.user)
        flash("Successfully signed in via %s" % blueprint.name, "alert alert-info")
        return False

    mail = info['email'] if 'email' in info else None
    name = info['name'] if 'name' in info else info['screen_name'] if 'screen_name' in info else None
    if current_user.is_authenticated:
        user = User.query.get(current_user.id)
    elif mail and name:
        user = User.query.filter(
            or_(User.email == mail, User.name == name)
        ).one_or_none()
    elif mail:
        user = User.query.filter(
            User.email == mail
        ).one_or_none()
    elif name:
        user = User.query.filter(
            User.name == name
        ).one_or_none()
    else:
        user = None

    if not user:
        name = info['name'] if ('name' in info and info['name']) else \
            info['screen_name'] if ('screen_name' in info and info['screen_name']) else \
                info['login'] if ('login' in info and info['login']) else ''.join(
                    random.choice(string.ascii_uppercase + string.digits) for _ in range(8))
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


def general_error(blueprint, error, error_description=None, error_uri=None):
    msg = (
        "OAuth error from {name}! "
        "error={error} description={description} uri={uri}"
    ).format(
        name=blueprint.name,
        error=error,
        description=error_description,
        uri=error_uri,
    )
    flash(msg, category="alert alert-danger")
