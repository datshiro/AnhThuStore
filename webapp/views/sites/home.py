from flask import render_template, request, flash, redirect
from flask_mongoengine.wtf import model_form
from mongoengine import NotUniqueError

from core.module import Module
from models.user import User
from webapp.forms import UserForm

module = Module('home', __name__)


@module.get('/')
def index():
    flash('Asfslkfjsf', 'sucess')
    flash('Asfslkfjsf', 'sucess')
    flash('Asfslkfjsf', 'warning')
    flash('Asfslkfjsf', 'sucess')

    return render_template('sites/home/index.html')


@module.get_post('/login')
def login():
    if request.method == 'POST':
        data = request.form
        username = data.get('username')
        password = data.get('password')

        user = User.authenticate(username, password)

        if not user:
            flash('Vui lòng kiểm tra lại user/mật khẩu', 'warning')

        else:
            session = request.session
            session.user = user
            session.save()
            return redirect(request.args.get('next', '/'))
    return render_template('sites/home/login.html')


@module.get_post('/register')
def register():
    form = UserForm(request.form)
    if request.method == 'POST' and form.validate():
        data = (request.form).to_dict()
        data.pop('csrf_token', None)
        username = data.get('username')
        password = data.get('password')
        try:
            user = User(**data)
            user.save()
        except NotUniqueError:
            flash('This username is existed!', 'error')
    return render_template('sites/home/register.html', form=form)
