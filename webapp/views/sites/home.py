from flask import render_template, request, flash, redirect, url_for
from flask_mongoengine.wtf import model_form
from mongoengine import NotUniqueError

from core.module import Module
from models.user import User
from webapp.forms import UserForm, RegisterForm

module = Module('home', __name__)


@module.get('/')
def index():
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
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        data = (request.form).to_dict()
        data.pop('csrf_token', None)
        try:
            user = User(**data)
            user.save()
        except NotUniqueError:
            flash('This username is existed!', 'error')
    return render_template('sites/home/register.html', form=form)


@module.get_post('/profile')
def profile():
    user = request.user
    form = UserForm(request.form, obj=user)
    if request.method == 'POST' and form.validate():
        form.populate_obj(user)
        data = (request.form).to_dict()
        data.pop('csrf_token', None)
        try:
            user.save()
            flash("Update Succeeded!", 'success')
        except NotUniqueError:
            flash('This username is existed!', 'error')
    return render_template('sites/home/profile.html', form=form)


@module.get('/logout')
def logout():
    session = request.session
    session.user = None
    session.save()
    flash("Log out succeeded!", 'success')
    return redirect(url_for('home.index'))
