# -*- coding: utf-8 -*-

from flask import Flask

from ca import CertificationAuthority
from common.constants import Ports

app = Flask(__name__)


@app.route("/gen_certificate", methods=["GET"])
def gen_certificate():
    ca_builder = CertificationAuthority()


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True, port=Ports.CA)
