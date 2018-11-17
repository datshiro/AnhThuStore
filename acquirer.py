# -*- coding: utf-8 -*-

from flask import Flask, request, abort
from flask_mongoengine import MongoEngine

import settings
from common.constants import Ports

app = Flask(__name__)
app.config.from_object(settings)
db = MongoEngine(app)


@app.route("/listen-and-forward", methods=["POST", "GET"])
def forward():
    if not request.form:
        abort(400)

    data = request.form.to_dict()
    bank_name = data.get('bank_name', None)
    authdata = data.get('authdata', None)


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True, port=Ports.ACQUIRER)
