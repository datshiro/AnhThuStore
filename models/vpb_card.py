# -*- coding: utf-8 -*-
import random
import string
from datetime import datetime
from mongoengine import *
from hashlib import md5


def id_generator(size=13, chars=string.ascii_uppercase + string.digits):
    id = "VPB" + ''.join(random.choice(chars) for _ in range(size))
    return id


class VPBBank(Document):
    id = StringField(primary_key=True, default=id_generator)
    email = EmailField(required=True, unique=True, max_length=255, verbose_name='Email')
    name = StringField(max_length=255, verbose_name='Tên đầy đủ')
    phone = StringField(max_length=255, verbose_name='Số điện thoại')
    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)
    password = StringField(required=True, max_length=255, verbose_name='Mật khẩu', default=id_generator(size=20))
    money = FloatField(min_value=0, default=100000, verbose_name='Số dư')

    def save(self, *args, **kwargs):
        super(VPBBank, self).save(args, kwargs)

    def topup(self, money):
        self.money += money
        self.save()


    @classmethod
    def authenticate(cls, card_id, password):
        try:
            card = VPBBank.objects.get(id=card_id, password=password)
            return card
        except DoesNotExist:
            return None
