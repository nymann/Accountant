from flask import Blueprint
from flask_restplus import Api

# Creating bluerpint
api_blueprint = Blueprint(
    'beverage_club_api',
    __name__
)

# Assigning blueprint to API
api = Api(api_blueprint)


# Beverage Club Namespace
from .ns_beeverage_club import api as bc_ns
api.add_namespace(bc_ns)

# Dinner Club Namespace
from .ns_dinner_club import api as dc_ns
api.add_namespace(dc_ns)

# User Namespcae
from .ns_user import api as u_ns
api.add_namespace(u_ns)


