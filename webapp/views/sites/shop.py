from flask import render_template

from core.module import Module

module = Module('shop', __name__, url_prefix='/shop')


@module.get('/')
def products():
    return render_template('sites/shop/index.html')
