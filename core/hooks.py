from flask import request, session
from mongoengine import DoesNotExist

from models.session import Session
from models.user import User
from services.keys import paymentgateway, merchant
from settings import SESSION_KEY, KUM, KUPG


def create_or_update_session():
    session_id = request.cookies.get(SESSION_KEY)
    session = None

    try:
        session = Session.objects.get(pk=session_id)

        session.update_datetime()
        session.save()
    except DoesNotExist:
        pass

    if not session:
        session = Session()
        session.save()

    request.session = session
    request.user = session.user


def set_session_cookie(response):
    response.set_cookie(SESSION_KEY, value=str(request.session.id))
    paymentgateway_publickey = paymentgateway.publickey()
    merchant_publickey = merchant.publickey()
    # response.set_cookie(KUM, merchant_publickey)
    # response.set_cookie(KUPG, paymentgateway_publickey)
    return response