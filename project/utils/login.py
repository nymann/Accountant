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
        flash("Failed to get user from %s" % blueprint.name, "alert alert-danger")
        return False
    info = resp.json()
    if 'id' in info:
        # facebook, GitHub
        user_id = info['id']
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
    else:
        mail = info['email'] if 'email' in info else None
        name = info['name'] if 'name' in info else info['screen_name'] if 'screen_name' in info else None
        if not name:
            print("Random Name OMEGALUL")
            name = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
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
