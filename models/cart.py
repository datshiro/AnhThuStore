from flask import request
import json


class Cart(object):
    data = {}

    def __init__(self, data):
        self.data = data

    @classmethod
    def get_current(cls):
        cookie_data = request.cookies.get('cart') or '{}'
        data = json.loads(cookie_data)
        return cls(data)

    @property
    def products_data(self):
        return self.data.get('products', {})

    @property
    def jsonified_data(self):
        return json.dumps(self.data)

    def add_product(self, product_id, quantity):
        data = self.products_data
        quantity_in_cart = data.get(product_id, 0)
        if quantity_in_cart:
            quantity += quantity_in_cart
        data[product_id] = quantity
        self.data['products'] = data

