from flask import render_template, request, flash, redirect

from core.module import Module
from models.user import User

module = Module('home', __name__)


@module.get('/')
def index():
    flash('Vui lòng kiểm tra lại user/mật khẩu', 'warning')
    return render_template('sites/home/index.html')


@module.get_post('/login')
def login():
    if request.method == 'POST':
        data = request.form
        email = data.get('email')
        password = data.get('password')

        user = User.authenticate(email, password)

        if not user:
            flash('Vui lòng kiểm tra lại user/mật khẩu', 'warning')

        else:
            session = request.session
            session.user = user
            session.save()
            return redirect(request.args.get('next', '/'))

    return render_template('sites/home/login.html')