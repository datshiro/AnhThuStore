# -*- coding: utf-8 -*-
from hashlib import md5
from mongoengine import *
from flask import url_for

# from core.base_model import BaseModel
from models.user_group import UserGroup
from models.store import Store
from services.image import gen_img_url
from datetime import datetime


class User(Document):
    USER = 1
    MOD = 2
    ADMIN = 3

    ROLE_CHOICES = (
        (USER, 'User'),
        (MOD, 'Moderator'),
        (ADMIN, 'Admin'),
    )

    USER_TYPE = 'user'
    ADMIN_TYPE = 'admin'
    AFFILIATE_TYPE = 'affiliate'
    DESIGN_TYPE = 'design'

    TYPE_CHOICES = (
        (USER_TYPE, 'User'),
        (ADMIN_TYPE, 'Admin'),
        (AFFILIATE_TYPE, 'Affiliate'),
        (DESIGN_TYPE, 'Design'),
    )

    FIELD_FORM = [
        'name', 'email',  'phone', 'store', 'user_type', 'province', 'district', 'address', 'group', 'image'
    ]

    uid = StringField()
    username = StringField(required=True, unique=True, max_length=255, verbose_name='Tên đăng nhập')
    group = ReferenceField('UserGroup', reverse_delete_rule=NULLIFY, verbose_name='Nhóm tài khoản')
    password = StringField(required=True, max_length=255, verbose_name='Mật khẩu')
    email = EmailField(required=True, unique=True, max_length=255, verbose_name='Email')
    name = StringField(max_length=255, verbose_name='Tên đầy đủ')
    phone = StringField(max_length=255, verbose_name='Số điện thoại')
    store = ReferenceField('Store', reverse_delete_rule=NULLIFY, verbose_name='Cửa hàng')
    user_type = StringField(default=USER_TYPE, choices=TYPE_CHOICES, verbose_name='Loại tài khoản')
    is_hidden = BooleanField(default=False)
    is_actived = BooleanField(default=False)
    district = ReferenceField('Districts', verbose_name='Quận / Huyện', null=True)
    address = StringField(verbose_name='Địa chỉ')
    province = ReferenceField('Provinces', verbose_name='Tỉnh / Thành phố', null=True)
    permission = IntField(required=True, default=1, choices=ROLE_CHOICES)
    sid = StringField()
    access_token = StringField()
    facebook_access_token = StringField()
    google_access_token = StringField()
    image = StringField(verbose_name='Ảnh đại diện')
    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)

    @classmethod
    def clean_data(cls, data):
        data['username'] = data['username'].encode('ascii', 'ignore').replace(' ', '')
        data['store'] = Store.objects.get(id=data['store'])
        data['group'] = UserGroup.objects.get(id=data['group'])
        return data

    @staticmethod
    def encrypt_password(password):
        if len(password) > 7:
            return md5(password.encode('utf-8')).hexdigest()
        raise ValidationError('Password\'s length should >= 8')

    @classmethod
    def authenticate(cls, email, password):
        try:
            password = cls.encrypt_password(password)
            user = User.objects.get(email=email, password=password)
            return user
        except DoesNotExist:
            return None

    def gen_img_url(self, size):
        if self.image is None or len(self.image) == 0:
            return gen_img_url(self.img, size)
        return None

    def get_avatar(self):
        try:
            default = url_for('static', filename='img/no-avatar.jpg')
            if self.image is not None and len(self.image) > 0:
                if "https://" in str(self.image):
                    return self.image
                return self.image_small_url
            else:
                return default
        except Exception:
            return ""





