# -*- coding: utf-8 -*-

from flask import Flask
from flask_mongoengine import MongoEngine

import settings
from common.constants import Ports

app = Flask(__name__)
app.config.from_object(settings)
db = MongoEngine(app)


@app.route("/gen-certificate", methods=["GET"])
def gen_certificate():
    pass


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True, port=Ports.CA)
