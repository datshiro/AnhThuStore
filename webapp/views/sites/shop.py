from flask import render_template, flash

from core.module import Module
from models.product import Product

module = Module('shop', __name__, url_prefix='/shop')


@module.get('/')
def shop():
    products = Product.objects.all()
    print(products)
    return render_template('sites/shop/index.html', products=products)
