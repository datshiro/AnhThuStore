# -*- coding: utf-8 -*-
import sys

from flask_admin import Admin
from flask_admin.contrib.mongoengine import ModelView
from flask_debugtoolbar import DebugToolbarExtension
from flask_mongoengine import MongoEngine
from flask_mail import Mail

from core.app import App
from importlib import reload

from models.card import Card
from vietcombank_app import settings

reload(sys)
mail = Mail()

app = App(__name__, template_folder='./vietcombank_app/templates', static_folder='./vietcombank_app/static')

app.config.from_object(settings)
db = MongoEngine(app)

toolbar = DebugToolbarExtension(app)
app.auto_add_template_filters()

admin = Admin(app, template_mode='bootstrap3')
admin.add_view(ModelView(Card, endpoint='Manage Card'))

mail.init_app(app)

from vietcombank_app.views import home
app.register_blueprint(home.module)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8003)