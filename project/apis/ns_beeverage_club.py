from flask_restplus import Namespace, Resource, fields, reqparse
from project.models import Beverage, BeverageBatch, User, BeverageUser, db
from sqlalchemy.exc import DBAPIError


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
@api.response(404, 'Beverage not found')
@api.param('beverage_id', 'The beverage identifier')
class BeverageOne(Resource):
    @api.doc('get_beverages')
    @api.marshal_with(beverage)
    def get(self, beverage_id):
        '''Get one Beverage'''

        return Beverage.query.get(beverage_id)


# Purchase a Beverage
@api.route('/<int:user_id>-<int:beverage_id>')
@api.response(400, 'Purchase cannot be made')
@api.param('user_id', 'The user identifier')
@api.param('beverage_id', 'The beverage identifier')
class PurchaseBeverage(Resource):
    @api.doc('purchase_beverage')
    @api.marshal_with(beverage)
    def post(self, user_id, beverage_id):
        '''Buy one beverage'''
        # Checks if the user is in our DB
        results = User.query.get(user_id)
        if results:

            # Check if beverage exists
            beverage = Beverage.query.get(beverage_id)
            if beverage:

                # Check if there are any left
                beverage_batch = BeverageBatch.query.filter(
                    BeverageBatch.quantity != 0
                ).filter_by(
                    beverage_id=beverage_id
                ).first()
                if beverage_batch:
                    # Handling beverage transaction
                    try:
                        # decrementing quantity
                        beverage_batch.quantity = beverage_batch.quantity - 1

                        # assigning beer
                        bought_beverage = BeverageUser(beverage_batch_id=beverage_batch.id, user_id=user_id)
                        db.session.add(bought_beverage)
                        db.session.commit()
                        return beverage
                    except DBAPIError as e:
                        db.session.rollback()
                        return {'message': 'Error: A beverage could not be bought. Try again or contact an admin'}, 400
                else:
                    return {'message': 'Error: It appears that there are no more beers left. Contact an admin.'}, 400
            else:
                return {'message': 'Error: Beverage does not exist.'}, 400
        else:
            return {'message': 'Error: User does not exist. Try again or contact an admin.'}, 400
