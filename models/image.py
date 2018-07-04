from datetime import datetime

from mongoengine import  *
from slugify import slugify


class Image(Document):
    name = StringField(max_length=255, verbose_name="Tên Hình ảnh")
    original = ImageField()
    big = ImageField(size=(1000, 1000, True))
    medium = ImageField(size=(500, 500, True))
    small = ImageField(size=(500, 500, True))
    created_at = DateTimeField(required=True, default=datetime.now)
    updated_at = DateTimeField(required=True, default=datetime.now)

