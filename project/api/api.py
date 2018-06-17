from project import api
from flask_restplus import Resource


@api.route('/hello', methods=['GET'])
class HelloWorld(Resource):
    def get(self):
        return {'hello': 'world'}
