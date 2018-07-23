# -*- coding: utf-8 -*-
from mongoengine import *


class OrderItem(Document):
    order = ReferenceField('Order')
    product = ReferenceField('Product', reverse_delete_rule=NULLIFY)
    product_id = ObjectIdField()
    product_sku = StringField()
    product_name = StringField()
    price = FloatField(min_value=0, default=0)
    price_input = FloatField(min_value=0, default=0)
    quantity = IntField(min_value=1, default=1)

    @property
    def subtotal(self):
        subtotal = 0
        if self is not None:
            subtotal += self.price * self.quantity
        return subtotal

    @property
    def profit(self):
        _profit= 0
        if self is not None:
            _profit= self.subtotal - (self.quantity * self.price_input)
        return _profit