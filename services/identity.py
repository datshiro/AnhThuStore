from functools import wraps

from flask import request, url_for
from werkzeug.utils import redirect


def login_required(f):
    @wraps(f)
    def decorated_function(*arg, **kwargs):
        session = request.session
        if session.user is None:
            return redirect(url_for('home.login', next=request.url))
        return f(*arg, **kwargs)
    return decorated_function