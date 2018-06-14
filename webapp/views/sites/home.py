from flask import render_template

from core.module import Module

module = Module('home', __name__)


@module.get('/')
def index():
    return render_template('sites/home/index.html')

