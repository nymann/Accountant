from flask_restplus import Namespace, Resource, fields, reqparse
from project.models import Beverage

# Creating the Namspace with desciption
api = Namespace('beverage_club', description='Beverage Club related operations')

# Setting up a model for how an answer is returned
beverage = api.model('Beverage', {
    'id': fields.String(required=True, description='The Beverage identifier'),
    'name': fields.String(required=True, description='The Beverage name'),
})


@api.route('/')
class BeverageList(Resource):
    @api.doc('beverages')
    @api.marshal_list_with(beverage)
    def get(self):
        '''List all Beverages'''
        return Beverage.query.all()


@api.route('/<int:beverage_id>')
@api.response(404, 'Cat not found')
@api.param('beverage_id', 'The beverage identifier')
class BeverageOne(Resource):
    @api.doc('get_beverages')
    @api.marshal_with(beverage)
    def get(self, beverage_id):
        '''Get one Beverage'''

        return Beverage.query.get(beverage_id)
