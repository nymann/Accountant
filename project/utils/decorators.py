from flask_login import current_user
import functools


def admin(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if current_user.admin:
            return func(*args, **kwargs)
    return wrapper
