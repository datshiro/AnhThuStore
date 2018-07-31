from flask import render_template, url_for, request
import requests
from core.module import Module
from models.product import Product

module = Module('product', __name__, url_prefix='/product')


@module.get('/<string:product_name>/<string:product_id>')
def detail(product_name, product_id):
    product = Product.objects.get(pk=product_id)
    # res = requests.get(request.host_url.rstrip('/') + url_for('home.index'))
    # print(res.content)
    return render_template('sites/shop/product_detail.html', product=product)