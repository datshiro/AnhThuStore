# -*- coding: utf-8 -*-
import sys

from flask_admin.contrib.mongoengine import ModelView
from flask_mongoengine import MongoEngine
from flask_debugtoolbar import DebugToolbarExtension

from core.app import App
from core.hooks import create_or_update_session, set_session_cookie
from importlib import reload
import settings
from flask_admin import Admin

from models.product import Product
from models.user import User
from models.user_group import UserGroup

reload(sys)

app = App(__name__, template_folder='./webapp/templates', static_folder='./webapp/static')
app.config.from_object(settings)
db = MongoEngine(app)

toolbar = DebugToolbarExtension(app)

admin = Admin(app, template_mode='bootstrap3')
admin.add_view(ModelView(User))
admin.add_view(ModelView(Product))
admin.add_view(ModelView(UserGroup))

app.auto_register_blueprint()

app.before_request(create_or_update_session)
app.after_request(set_session_cookie)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8000)
