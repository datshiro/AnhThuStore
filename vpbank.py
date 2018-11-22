# -*- coding: utf-8 -*-
import sys

from flask_admin import Admin
from flask_admin.contrib.mongoengine import ModelView
from flask_debugtoolbar import DebugToolbarExtension
from flask_mongoengine import MongoEngine
from flask_mail import Mail

from common.constants import Ports
from core.app import App
from importlib import reload

from models.vcb_card import VCBBank
from vietcombank_app import settings

reload(sys)
mail = Mail()

app = App(__name__, template_folder='./vpbank_app/templates', static_folder='./webapp/static')

app.config.from_object(settings)
db = MongoEngine(app)

app.auto_add_template_filters()

admin = Admin(app, template_mode='bootstrap3')
admin.add_view(ModelView(VCBBank, endpoint='Manage VCBBank'))

mail.init_app(app)

from vpbank_app.views import home, api

app.register_blueprint(home.module)
app.register_blueprint(api.module)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=Ports.VPB_BANK)
