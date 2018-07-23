from json import dumps

from flask import request, make_response, Response

from core.module import Module

module = Module('api', __name__, url_prefix='/api')


@module.get_post('/make_purchase_request')
def make_purchase_request():
    data = request.form.to_dict()
    print(data)
    response = make_response(json({'status': 'OK'}))
    return response


def json(data):
    """
    This is the function, which return json data
    """
    return Response(dumps({'data': data}), mimetype='application/json')
