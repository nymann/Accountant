import functools

from flask import url_for, redirect, flash
from flask_login import current_user


def admin(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.admin:
            flash("Only admin users can access that page.", "alert alert-danger")
            return redirect(url_for('site.index'))
        return func(*args, **kwargs)

    return wrapper


def active(func):
    @functools.wraps(func)
    def wrappwer(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.active:
            flash("Only active residents can access that page.", "alert alert-danger")
            return redirect(url_for('site.index'))
        return func(*args, **kwargs)

    return wrappwer
