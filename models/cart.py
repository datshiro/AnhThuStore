from flask import request
import json

from models.product import Product


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

    def remove_product(self, product_id):
        data = self.products_data
        data.pop(product_id)
        self.data['products'] = data

    @property
    def sum_value(self):
        products = self.products_data
        sum = 0
        for k,v in products.items():
            product = Product.objects.get(pk=k)
            sum += (product.price * v)
            product.quantity -= v
            product.save()
        return sum

    @property
    def products(self):
        products = []
        for k, v in self.products_data.items():
            product = Product.objects.get(pk=k)
            products.append(product)
        return products