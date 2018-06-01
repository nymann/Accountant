from flask_login import current_user


def is_admin():
    return current_user.is_authenticated and current_user.admin


def is_active():
    return current_user.is_authenticated and current_user.active
