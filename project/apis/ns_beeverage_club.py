from flask_restplus import Namespace, Resource, fields, reqparse
from project.models import Beverage, db


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
        # return db.session.query(Beverage).query.all()

@api.route('/byid')
class Beverage(Resource):
    @api.doc('beverages')
    @api.marshal_list_with(beverage)
    def post(self):
        '''Get one Beverage'''
        parser = reqparse.RequestParser()
        parser.add_argument('beverage_id', type=int, help='The id of the beverage you want')
        beverage_id = parser.parse_args()
        return Beverage.query.get(beverage_id)
