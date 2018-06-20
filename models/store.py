# -*- coding:utf-8 -*-
from mongoengine import *
from flask_mongoengine import Document
from datetime import datetime

# from models.contact import Contact  # Mandatory for ReferenceField


class Store(Document):
    name = StringField(verbose_name='Tên cửa hàng', max_length=255, required=True, unique=True)
    parent = ReferenceField('Store', verbose_name='Hệ thống', reverse_delete_rule=NULLIFY)
    contact = ReferenceField('Contact', reverse_delete_rule=NULLIFY)
    address = StringField(verbose_name='Địa chỉ cửa hàng', max_length=255)
    phone = StringField(verbose_name='Số điện thoại', max_length=20)
    created_at = DateTimeField(default=datetime.utcnow)
    listsp = ListField(ReferenceField('Warehouse'))
    is_hidden = BooleanField(default=False)

    @property
    def get_created_at(self):
        return str(self.created_at.day)+"/"+str(self.created_at.month)+"/"+str(self.created_at.year)

    @classmethod
    def get_top_level_stores(cls):
        stores = cls.objects()
        return [n for n in stores if n.get_level() == 0]

    def get_childs(self):
        return Store.objects(parent=self.id, is_hidden__in=[None, False]).order_by('no')

    def get_level(self):
        def check_level(le, category):
            if category is not None:
                if category.parent is None:
                    return le
            else:
                return le
            return check_level(le+1, category.parent)
        if self.parent is None:
            return 0
        return check_level(0, self)

    def __unicode__(self):
        return self.name
