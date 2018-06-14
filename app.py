# -*- coding: utf-8 -*-
import sys

from flask_mongoengine import MongoEngine
from flask_debugtoolbar import DebugToolbarExtension

from core.app import App
from importlib import reload
import settings

reload(sys)

app = App(__name__, template_folder='./webapp/templates', static_folder='./webapp/static')
app.config.from_object(settings)

toolbar = DebugToolbarExtension(app)
db = MongoEngine(app)


app.auto_register_blueprint()

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8000)
