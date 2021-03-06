# -*- coding: utf-8 -*-
import sys

from flask_admin.contrib.mongoengine import ModelView
from flask_mail import Mail
from flask_mongoengine import MongoEngine
from flask_debugtoolbar import DebugToolbarExtension

from common.constants import Ports
from core.app import App
from core.hooks import create_or_update_session, set_session_cookie
from importlib import reload
import settings
from flask_admin import Admin

from models.vcb_card import VCBBank
from models.certificate_key import CertificateKey
from models.product import Product
from models.user import User
from models.user_group import UserGroup
from models.vpb_card import VPBBank

reload(sys)
mail = Mail()

app = App(__name__, template_folder='./webapp/templates', static_folder='./webapp/static')
app.config.from_object(settings)
db = MongoEngine(app)
mail.init_app(app)

toolbar = DebugToolbarExtension(app)

admin = Admin(app, template_mode='bootstrap3')
admin.add_view(ModelView(User, endpoint='Manage User'))
admin.add_view(ModelView(Product, endpoint='Manage Product'))
admin.add_view(ModelView(UserGroup, endpoint='User Group'))
admin.add_view(ModelView(VCBBank, endpoint='VCB Cards'))
admin.add_view(ModelView(VPBBank, endpoint='VPB Cards'))
admin.add_view(ModelView(CertificateKey, endpoint='Certificate Key'))

app.auto_register_blueprint()

app.before_request(create_or_update_session)
app.after_request(set_session_cookie)

app.auto_add_template_filters()

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=Ports.MERCHANT, ssl_context=('cert.pem', 'key.pem'))
