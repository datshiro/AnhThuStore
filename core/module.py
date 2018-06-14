from functools import wraps

from flask import Blueprint


class Module(Blueprint):
    def __init__(self, *args, **kwargs):
        super(Module, self).__init__(*args, **kwargs)

    def _add_route(self, rule, methods, perm, **options):
        def decorator(f):
            endpoint = options.pop("endpoint", f.__name__)
            self.add_url_rule(rule, endpoint, f, methods=methods, **options)
            return f
        return decorator

    def get_post(self, rule, perm=None, **options):
        return self._add_route(rule, ['GET', 'POST'], perm, **options)

    def get(self, rule, perm=None, **options):
        return self._add_route(rule, ['GET'], perm, **options)

    def post(self, rule, perm=None, **options):
        return self._add_route(rule, ['POST'], perm, **options)

    def delete(self, rule, perm=None, **options):
        return self._add_route(rule, ['DELETE'], perm, **options)