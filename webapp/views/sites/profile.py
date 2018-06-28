from flask import request, session

from core.module import Module

module = Module('profile', __name__, url_prefix='/profile')


@module.get('/')
def info():
    print()
    return 'User Info'
