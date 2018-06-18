from functools import wraps

from flask import Blueprint, request
from flask_restplus import Api

# Creating bluerpint
api_blueprint = Blueprint(
    'beverage_club_api',
    __name__
)

# Security
authorizations = {
    'apikey': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'X-API-KEU'
    }
}

# Assigning blueprint to API
api = Api(api_blueprint, authorization=authorizations)


# Decorations
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if 'X-API-KEY' in request.headers:
            token = request.headers['X-API-KEY']

        if not token:
            return {'message': 'Token is missing.'}

        return f(*args, **kwargs)

    return decorated()


# Beverage Club Namespace
from .ns_beeverage_club import api as bc_ns
api.add_namespace(bc_ns)

# Dinner Club Namespace
from .ns_dinner_club import api as dc_ns
api.add_namespace(dc_ns)

# User Namespcae
from .ns_user import api as u_ns
api.add_namespace(u_ns)


