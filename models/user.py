# -*- coding: utf-8 -*-
from hashlib import md5
from mongoengine import *
from models.user_group import UserGroup
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
    DESIGN_TYPE = 'design'

    TYPE_CHOICES = (
        (USER_TYPE, 'User'),
        (ADMIN_TYPE, 'Admin'),
        (DESIGN_TYPE, 'Design'),
    )

    username = StringField(required=True, unique=True, max_length=255, verbose_name='Tên đăng nhập')
    group = ReferenceField('UserGroup', reverse_delete_rule=NULLIFY, verbose_name='Nhóm tài khoản')
    password = StringField(required=True, max_length=255, verbose_name='Mật khẩu')
    email = EmailField(required=True, unique=True, max_length=255, verbose_name='Email')
    name = StringField(max_length=255, verbose_name='Tên đầy đủ')
    phone = StringField(max_length=255, verbose_name='Số điện thoại')
    user_type = StringField(default=USER_TYPE, choices=TYPE_CHOICES, verbose_name='Loại tài khoản')
    permission = IntField(required=True, default=1, choices=ROLE_CHOICES)
    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)

    @classmethod
    def clean_data(cls, data):
        data['username'] = data['username'].encode('ascii', 'ignore').replace(' ', '')
        data['group'] = UserGroup.objects.get(id=data['group'])
        return data

    def save(self, *args, **kwargs):
        self.password = self.encrypt_password(self.password)
        super(User, self).save(args, kwargs)

    @staticmethod
    def encrypt_password(password):
        if len(password) > 7:
            return md5(password.encode('utf-8')).hexdigest()
        raise ValidationError('Password\'s length should >= 8')

    @classmethod
    def authenticate(cls, username, password):
        try:
            password = cls.encrypt_password(password)
            user = User.objects.get(username=username, password=password)
            return user
        except DoesNotExist:
            return None