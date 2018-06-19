from flask_restplus import Namespace, Resource, fields
from project.models import Dinner

api = Namespace('dinner_club', description='Dinner Club related operations')

dinner_club = api.model('Dinner', {
    'id': fields.String(required=True, description='The Dinner identifier')
})


@api.route('/')
class DinnerList(Resource):
    @api.doc('dinners')
    @api.marshal_list_with(dinner_club)
    def get(self):
        '''Get Dinner List'''
        return Dinner.query.all()
