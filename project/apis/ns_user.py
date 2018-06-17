from flask_restplus import Namespace, Resource, fields
from project.models import User

api = Namespace('user', description='User related operations')

user = api.model('user', {
    'id': fields.String(required=True, description='The User identifier'),
    'name': fields.String(required=True, description='The Users name'),
})


@api.route('/')
class UserList(Resource):
    @api.doc('users')
    @api.marshal_list_with(user)
    def get(self):
        '''Get User List'''
        return User.query.all()


@api.route('/<int:user_id>')
@api.response(404, 'User not fount')
@api.param('user_id', "The User identifier")
class UserOne(Resource):
    @api.doc('get_user')
    @api.marshal_with(user)
    def get(self, user_id):
        '''Get One User'''
        return User.query.get(user_id)
