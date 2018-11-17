# -*- coding: utf-8 -*-

from flask_mongoengine import MongoEngine
import settings
from flask import Flask, request, make_response
from services.ca import CertificationAuthority
from common.constants import Ports
from services.converter import json as custom_json

app = Flask(__name__)
app.config.from_object(settings)
db = MongoEngine(app)


@app.route("/gen-certificate", methods=["GET"])
def gen_certificate():
    #Get init info of client
    data = request.form.to_dict()
    prefix = data.get('use_type')
    common_name = unit_name = data.get('owner')
    ca_builder = CertificationAuthority()
    #fix ca-cert to ca-"username or bank,..."
    ca_builder.create_certificate('ca-{}'.format(prefix), common_name, unit_name)
    private_key = ca_builder.get_private_key()
    public_key = ca_builder.get_public_key()
    return make_response(custom_json(
        {'public_key': public_key.decode().strip(), 'private_key': private_key.decode().strip()}))

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True, port=Ports.CA)
