from flask import render_template, request, url_for
from flask_mail import Message
from werkzeug.utils import redirect

from core.module import Module
from models.vpb_card import VPBBank, NotUniqueError
from vietcombank_app.forms import RegisterForm

module = Module('home', __name__)


@module.get_post('/')
def index():
    if request.method == 'POST':
        data = request.form
        card_id = data.get('card-id')
        password = data.get('password')

        card = VPBBank.authenticate(card_id, password)
        if card:
            return render_template('profile.html', card=card)
    return render_template('index.html')


@module.get_post('/register')
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        data = (request.form).to_dict()
        data.pop('csrf_token', None)

        card = VPBBank(**data)
        card.save()

        from vietcombank import mail
        msg = render_template('register-email.html', card=card)
        message = Message(subject="Đăng ký thành công thẻ VPB-EMILIOANH",
                          html=msg,
                          sender=("VPB-Emilio Anh", "datshiro@gmail.com"),
                          recipients=[card.email])
        mail.send(message)
        return render_template('index.html')

    return render_template('register.html', form=form)


@module.get_post('/topup')
def topup():
    if request.method == "POST":
        data = request.form
        card_id = data.get('card-id')
        topup_amount = data.get('topup-money')

        card = VPBBank.objects.get(pk=card_id)
        card.topup(float(topup_amount))
    return redirect(url_for('home.index'))
