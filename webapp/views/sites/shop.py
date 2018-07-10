from flask import render_template, flash, request, url_for, make_response
from werkzeug.utils import redirect

from core.module import Module
from models.cart import Cart
from models.product import Product, DoesNotExist
from services import identity


module = Module('shop', __name__, url_prefix='/shop')


@module.get('/')
def shop():
    products = Product.objects.all()
    return render_template('sites/shop/index.html', products=products)


@module.post('/add-to-cart/<string:product_id>&<int:quantity>')
def add_to_cart(product_id, quantity):
    try:
        cart = Cart.get_current()
        cart.add_product(product_id, quantity)
        response = make_response()
        response.set_cookie('cart', cart.jsonified_data)

        flash("Add succeeded!", 'success')
        return response
    except DoesNotExist:
        flash("Does Not Exist", 'error')


@module.get_post('/checkout')
def checkout():
    if request.session.user is None:
        return redirect(url_for('home.login', next=request.url))
    return render_template('sites/shop/checkout.html')