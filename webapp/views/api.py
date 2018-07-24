from json import dumps

from flask import request, make_response, Response

from core.module import Module
from services.converter import bytes_to_array, hex_to_bytes, hex_to_array

module = Module('api', __name__, url_prefix='/api')


@module.get_post('/make_purchase_request')
def make_purchase_request():
    data = request.form.to_dict()
    print(data)
    key = data.get('key')
    iv = data.get('iv')
    pomd = data.get('pomd')
    oi = data.get('oi')
    key = hex_to_array(key)
    iv = hex_to_array(iv)
    pomd = hex_to_array(pomd)

    print(key)
    print(iv)
    print(pomd)

    print(oi)
    response = make_response(json({'status': 'OK'}))
    return response


def json(data):
    """
    This is the function, which return json data
    """
    return Response(dumps({'data': data}), mimetype='application/json')
