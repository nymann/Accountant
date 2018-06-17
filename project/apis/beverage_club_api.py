from flask_restplus import Resource, Namespace

api = Namespace('beverage_club', description='Beverage Clubs')


@api.route('/hello', methods=['GET'])
class HelloWorld(Resource):
    def get(self):
        return {'hello': 'world'}
