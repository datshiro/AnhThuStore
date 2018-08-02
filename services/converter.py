import base64
from json import dumps

from flask import Response


def bytes_to_array(b):
    hex_string = b.hex()
    decimal_array = []
    for c in range(0, len(hex_string), 2):
        c = (hex_string[c] + hex_string[c + 1])
        decimal_array.append(int(c,16))
    return decimal_array


def hex_to_bytes(hex_string):
    if hex_string is None:
        return ""
    return bytes([b for b in bytearray.fromhex(hex_string)])

def hex_to_array(hex_string):
    if hex_string is None:
        return ""
    return [b for b in bytearray.fromhex(hex_string)]


def decodeBase64(string):
    return base64.b64decode(string)


def encodeBase64(bytestring):
    return base64.b64encode(bytestring)

def json(data):
    """
    This is the function, which return json data
    """
    return Response(dumps({'data': data}), mimetype='application/json')
