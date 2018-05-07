from . import api


@api.route('/')
def index():
    return "{results: bla}"
