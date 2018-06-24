# -*- coding: utf-8 -*-
from mongoengine import *
from datetime import datetime

from core.base_model import BaseModel
from services.image import process_thumbnail
from slugify import slugify


class Image(BaseModel):
    name = StringField(max_length=255, verbose_name="Tên Hình ảnh")
    link = StringField(max_length=255, verbose_name="Link Hình ảnh")
    original = ImageField()
    big = ImageField(size=(1000, 1000, True))
    medium = ImageField(size=(500, 500, True))
    small = ImageField(size=(500, 500, True))
    author = ReferenceField('User')
    category = ReferenceField('Category')
    created_at = DateTimeField(required=True, default=datetime.now)
    updated_at = DateTimeField(required=True, default=datetime.now)

    def save_image(self, f):
        ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif', 'JPG'])
        ext = f.filename.rsplit('.', 1)[1]

        if ext in ALLOWED_EXTENSIONS:
            process_thumbnail(f)

            self.original = self.big = self.medium = self.small = f

            # save link
            a = datetime.today()
            name = f.filename.rsplit('.', 1)[0]
            link = slugify(name + '-' + str(a.day) + '-' + str(a.month) + '-' + str(a.year))
            self.name = name
            self.link = link
            self.created_at = datetime.now()

            # save data
            self.save()
            return self

        return None

    @property
    def get_created_at(self):
        return str(self.created_at.day)+'/'+str(self.created_at.month)+'/'+str(self.created_at.year) + ' | ' + str(self.created_at.hour) +':'+str(self.created_at.minute)