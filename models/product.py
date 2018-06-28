# -*- coding: utf-8 -*-
from mongoengine import *

from datetime import datetime
import time
import random
import string


def gen_object_id():
    return ''.join(time.ctime().split(' ')).replace(':', '').upper()


def id_generator(size=13, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


class Product(Document):
    id = StringField(primary_key=True, default=gen_object_id)
    name = StringField(required=True, verbose_name='Tên sản phẩm', max_length=500)
    description = StringField(verbose_name='Giới thiệu sản phẩm')
    created_at = DateTimeField(required=True, default=datetime.now)
    updated_at = DateTimeField(required=True, default=datetime.now)
    price_input = FloatField(min_value=0, default=0, verbose_name='Giá nhập sản phẩm')
    price = FloatField(min_value=0, default=0, verbose_name='Nhập giá bán')
    quantity = IntField(min_value=0, default=0, verbose_name='Số Lượng')


    @property
    def status(self):
        return "Còn hàng" if self.quantity > 0 else "Hết hàng"

    @property
    def in_warehouse(self):
        return self.quantity


    @property
    def humanized_price(self):
        return "{:,.0f}".format(self.price)

    @property
    def humanized_price_input(self):
        return "{:,.0f}".format(self.price_input)

    @property
    def is_available(self):
        return self.quantity > 0

    @property
    def get_quantity(self):
        return self.quantity

    @classmethod
    def get_last(cls, limit=10):
        return cls.objects().order_by('-created_at').limit(limit)

    @classmethod
    def get_all(cls):
        return cls.objects().order_by('-created_at')



