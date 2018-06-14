import os
from importlib import import_module
from os import path, listdir
from os.path import dirname

from flask import Flask, abort


class App(Flask):
    def auto_register_blueprint(self):
        """ Auto scan and register blueprints """
        views_path = path.join(dirname(dirname(__file__)), 'webapp', 'views')
        sites_path = path.join(views_path, 'sites')

        self._register('sites', sites_path)

    def _register(self, segment, segment_path):
        for item in listdir(segment_path):
            if '__init__' in item or '.pyc' in item:
                continue
            if '.py' not in item:
                continue

            mod_name = item.split('.')[0]
            mod_str = 'webapp.views.{}.{}'.format(segment,mod_name)
            mod = import_module(mod_str)
            blueprint = getattr(mod, 'module')

            self.register_blueprint(blueprint)