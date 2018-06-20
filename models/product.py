# -*- coding: utf-8 -*-
from mongoengine import *

from models.image import Image
from models.news import News
from datetime import datetime, date
import random
import string
from hashlib import md5
import urllib.request, urllib.parse, urllib.error, hashlib
from services.image import image_url, image_original_url, image_small_url


class Product(Document):
    name = StringField(required=True, verbose_name='Tên sản phẩm', max_length=500)
    link = StringField(required=True, unique=True, verbose_name='URL', max_length=500)
    video = StringField(verbose_name='Đường Link, ID Youtube', max_length=255)
    short_description = StringField(verbose_name='Giới thiệu ngắn', max_length=500)
    sku = StringField(required=True, verbose_name='Mã SKU sản phẩm', max_length=255)
    view = IntField(default=0)
    order = IntField(default=0)
    description = StringField(verbose_name='Giới thiệu sản phẩm')
    author = ReferenceField('User', reverse_delete_rule=NULLIFY)
    category = ListField(ReferenceField('Category', reverse_delete_rule=NULLIFY), verbose_name='Danh Mục')
    news = ListField(ReferenceField('News', reverse_delete_rule=NULLIFY), verbose_name='Bài Viết Liên Quan')
    product_type_detail = ListField(ReferenceField('Product_type_detail'))
    brand = ReferenceField('Brand', reverse_delete_rule=NULLIFY, verbose_name='Thương Hiệu')
    created_at = DateTimeField(required=True, default=datetime.now)
    updated_at = DateTimeField(required=True, default=datetime.now)
    price_input = FloatField(min_value=0, default=0, verbose_name='Giá nhập sản phẩm')
    profit = FloatField(default=0, min_value=0, max_value=70)
    vat = IntField(min_value=0, default=0, verbose_name='Thuế VAT')
    price = FloatField(min_value=0, default=0, verbose_name='Nhập giá bán')
    selling_price = FloatField(min_value=0, default=0, verbose_name='Giảm giá còn')
    discount = FloatField(min_value=0, max_value=100, default=0, verbose_name='Giảm Theo %')
    is_hidden = BooleanField(default=False)
    is_landing_page = BooleanField(default=False)
    landing_page = StringField()
    image = StringField()
    images = ListField(ReferenceField('Image', reverse_delete_rule=NULLIFY))
    meta_title = StringField(verbose_name='SEO tiêu đề', max_length=255)
    meta_keywords = ListField(StringField(), verbose_name='SEO Từ khóa')
    meta_description = StringField(verbose_name='SEO Description')

    FORM_FIELD = [
        'name',
        'link',
        'short_description',
        'description',
        'video',
        'sku',
        'category',
        'news',
        'price_input',
        'price',
        'selling_price',
        'discount',
        'vat',
        'brand',
        'meta_title',
        'meta_keywords',
        'meta_description',
        'image',
        'images'
    ]

    @property
    def image_urls(self):
        images = [{'small': image_small_url(image.id), 'thumbnail': image_url(
            image.id), 'original': image_original_url(image.id), 'object_id': image.id} for image in self.images]
        return images

    @property
    def image_url(self):
        if self.image is None or len(self.image) == 0:
            return ""
        return image_url(self.image)

    @property
    def image_original_url(self):
        if self.image is None or len(self.image) == 0:
            return ""
        return image_original_url(self.image)

    @property
    def image_small_url(self):
        if self.image is None or len(self.image) == 0:
            return ""
        return image_small_url(self.image)

    @property
    def status(self):
        from models.warehouse import Warehouse
        try:
            waweh = Warehouse.objects.get(product=self.id)
            return "Còn hàng" if waweh.quantity > 0 else "Hết hàng"
        except Exception as e:
            return "Đã Hết Hàng"

    @property
    def in_warehouse(self):
        from models.warehouse import Warehouse
        try:
            waweh = Warehouse.objects.get(product=self.id)
            return waweh.quantity
        except Exception as e:
            return 0

    @property
    def brand_name(self):
        return self.brand.name if self.brand.name else ""

    @property
    def warehouseId(self):
        try:
            from models.warehouse import Warehouse
            return Warehouse.objects.get(product=self.id).id
        except Exception as e:
            return ""


    @property
    def humanized_price(self):
        return "{:,.0f}".format(self.price)

    @property
    def humanized_price_input(self):
        return "{:,.0f}".format(self.price_input)

    @property
    def huma_price(self):
        return "{:,.0f}".format(self.price)

    @property
    def humanized_selling_price(self):
        return "{:,.0f}".format(self.selling_price)

    @property
    def humanized_discount(self):
        return "- {0} %".format(self.discount)

    @property
    def get_vat(self):
        return " {0} %".format(self.vat)

    @property
    def isInWarehouse(self):
        from models.warehouse import Warehouse
        return Warehouse.objects(product=self.id).count() > 0

    def products_same(self, count, order_by):
        return Product.objects(is_hidden__nin=[True], category__in=self.category).order_by(order_by).limit(count)

    @property
    def quantityInWarehouse(self):
        from models.warehouse import Warehouse
        try:
            quantity = 0
            for i in Warehouse.objects(product=self.id):
                quantity = quantity + i.quantity
            return quantity
        except Exception as e:
            pass
        return 0

    @classmethod
    def get_last(cls, limit=10):
        return cls.objects().order_by('-created_at').limit(limit)

    @classmethod
    def get_all(cls):
        return cls.objects().order_by('-created_at')

    @classmethod
    def get_best_sellers(cls, limit=8):
        return cls.objects().order_by('-order').limit(limit)

    @classmethod
    def genSKU(cls):
        exist = True
        sku = str(id_generator(13))
        while exist:
            if Product.objects(sku=sku).count() == 0:
                exist = False
            else:
                sku = str(id_generator(13))
        return sku

    def quantity_in_store(self, store):
        from models.warehouse import Warehouse
        try:
            quantity = 0
            for i in Warehouse.objects(product=self.id, store=store):
                quantity = quantity + i.quantity
            return quantity
        except Exception as e:
            pass
        return 0


def id_generator(size=13, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def genSKU():
    exist = True
    sku = str(id_generator(13))
    while exist:
        if Product.objects(sku=sku).count() == 0:
            exist = False
        else:
            sku = str(id_generator(13))
    return sku

def validate_link(link, product_id):
    return False if Product.objects(link=link, id__nin=[product_id]).first() is not None else True
