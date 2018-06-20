# -*- coding: utf-8 -*-
from mongoengine import *

from flask_mongoengine import Document
from models.product import Product
from models.store import Store
from datetime import *


class Warehouse(Document):
    product = ReferenceField('Product', reverse_delete_rule=NULLIFY)
    quantity = IntField(default=0, verbose_name='Số lượng')
    store = ReferenceField('Store', reverse_delete_rule=NULLIFY)
    parent = ReferenceField('Warehouse', reverse_delete_rule=NULLIFY)
    created_at = DateTimeField(default=datetime.now)

    @property
    def get_created_at(self):
        return str(self.created_at.day)+"/"+str(self.created_at.month) + \
            "/"+str(self.created_at.year)+" | "+str(self.created_at.hour) + \
            ":"+str(self.created_at.minute)
