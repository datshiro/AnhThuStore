from flask import render_template

from core.module import Module
from models.product import Product

module = Module('product', __name__, url_prefix='/product')


@module.get('/<string:product_name>/<string:product_id>')
def detail(product_name, product_id):
    product = Product.objects.get(pk=product_id)
    return render_template('sites/shop/product_detail.html', product=product)