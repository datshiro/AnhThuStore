from flask import render_template, flash, request, url_for, make_response
from werkzeug.utils import redirect

from common.constants import CertificateOwner, CertificateType
from core.module import Module
from models.cart import Cart
from models.product import Product, DoesNotExist
from services import identity
from services.keys import get_key

module = Module('shop', __name__, url_prefix='/shop')


@module.get('/')
def shop():
    products = Product.objects.all()
    return render_template('sites/shop/index.html', products=products)


@module.post('/add-to-cart/<string:product_id>&<int:quantity>')
def add_to_cart(product_id, quantity):
    cart = Cart.get_current()
    cart.add_product(product_id, quantity)
    response = make_response()
    response.set_cookie('cart', cart.jsonified_data)
    flash("Add succeeded!", 'success')
    return response


@module.post('/remove-from-cart/<string:product_id>')
def remove_from_cart(product_id):
    cart = Cart.get_current()
    cart.remove_product(product_id)
    response = make_response()
    response.set_cookie('cart', cart.jsonified_data)

    flash("Remove succeeded!", 'success')
    return response


@module.get_post('/cart')
def show_cart():
    # if request.session.user is None:
    #     return redirect(url_for('home.login', next=request.url))
    cart = Cart.get_current()
    products = cart.products

    if request.method == 'POST':
        pass
    return render_template('sites/shop/cart.html', products=products, cart=cart)


@module.get_post('/checkout')
@identity.login_required
def checkout():
    cart = Cart.get_current()
    oi = cart
    oi.data['total'] = cart.sum_value
    oi = oi.jsonified_data
    merchant_publickey = get_key(CertificateOwner.MERCHANT, CertificateType.MERCHANT)['public_key']
    paymentgateway_publickey = get_key(CertificateOwner.GATEWAY, CertificateType.GATEWAY)['public_key']

    products = cart.products
    return render_template('sites/shop/checkout.html', products=products, cart=cart, oi=oi, kum=merchant_publickey, kupg=paymentgateway_publickey)
