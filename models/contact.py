# -*- coding: utf-8 -*-
from mongoengine import *
from models.provinces import Provinces
from models.districts import Districts
from datetime import *


class Contact(Document):
    name = StringField(required=True, unique=True, max_length=255, verbose_name='Tên liên hệ')
    mapping = ReferenceField('Map', verbose_name='Contact in google map', null=True)
    phone = StringField(max_length=255, verbose_name='Số điện thoại liên hệ')
    province = ReferenceField('Provinces', verbose_name='Tỉnh / Thành phố', null=True)
    district = ReferenceField('Districts', verbose_name='Quận / Huyện', null=True)
    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)

