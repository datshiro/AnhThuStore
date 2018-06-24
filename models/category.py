# -*- coding: utf-8 -*-
# import xlrd
# import xlwt
import math
import io
from flask import request
from mongoengine import *
from slugify import slugify
from services.image import image_url, image_original_url, image_small_url


LIST_STATUS = ['products', 'news', 'videos', 'services', 'promotions', 'static_page', 'human']


class Category(Document):
    name = StringField(required=True, max_length=255, verbose_name='Tên danh mục')
    description = StringField(verbose_name='Giới thiệu về danh mục')
    parent = ReferenceField('Category', reverse_delete_rule=NULLIFY, verbose_name='Các danh mục', null=True)
    image = StringField()
    banner = StringField()
    status = StringField(default='products')
    link = StringField(required=True, unique=True, verbose_name='Đường dẫn URL', max_length=255)
    no = IntField(required=True, default=0,  verbose_name='Vị trí')
    is_hidden = BooleanField(default=False)
    is_special_category = BooleanField(default=False)
    meta_description = StringField(null=True, verbose_name='Mô tả SEO')
    meta_keywords = ListField(StringField(max_length=255), verbose_name='Mô tả SEO từ khóa')
    meta_title = StringField(null=True, verbose_name='Mô tả SEO tiêu đề', max_length=255)

    @classmethod
    def clean_data(cls, data):
        data['link'] = data['link'].encode('ascii', 'ignore').replace(' ', '-')
        data['meta_keywords'] = [i for i in data['meta_keywords'].split(',') if i != ''] if data['meta_keywords'] else []
        data['parent'] = Category.objects.get(id=data['parent']) if data['parent'] else ''
        return data

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
    def image_banner_url(self):
        if self.banner is None or len(self.banner) == 0:
            return ""
        return image_url(self.banner)

    @property
    def image_banner_original_url(self):
        if self.banner is None or len(self.banner) == 0:
            return ""
        return image_original_url(self.banner)

    @property
    def image_banner_small_url(self):
        if self.banner is None or len(self.banner) == 0:
            return ""
        return image_small_url(self.banner)

    def get_childs(self):
        return Category.objects(parent=self.id, is_hidden__ne=True).order_by('no')

    def get_childs_category_admin(self):
        return Category.objects(parent=self.id, status='products').order_by('no')

    def get_level(self):
        def check_level(le, category):
            if category is None or category.parent is None:
                return le

            return check_level(le+1, category.parent)

        if self.parent is None:
            return 0

        return check_level(0, self)

    def get_root(self):
        def get_parent(category):
            if category is None or category.parent is None:
                return category
            return get_parent(category.parent)

        return get_parent(self)

    # def get_slider(self, position):
    #     from models.slider import Slider
    #     try:
    #         slider = Slider.objects(category=self.id, position=position).first()
    #         if slider:
    #             return slider
    #         return None
    #     except Exception as e:
    #         return None

    def get_siblings(self):
        categories = []
        try:
            categories = self.get_childs() if self.parent is None else self.parent.get_childs()
        except Exception as e:
            pass
        return categories

    def get_item_count(self, status):
        categories = [self.id]
        if self.get_childs() is not None and len(self.get_childs()) > 0:
            for item in self.get_childs():
                categories.append(item.id)
                if item.get_childs() is not None and len(item.get_childs()) > 0:
                    for x in item.get_childs():
                        categories.append(x.id)
        if status == 'products' :
            from models.product import Product
            return Product.objects(category__in=categories, is_hidden__nin=[True]).count()
        elif status == 'news':
            from models.news import News
            return News.objects(status=status, category__in=categories, is_hidden__nin=[True]).count()
        elif status == 'videos':
            from models.video import Video
            return Video.objects(category__in=categories, is_hidden__nin=[True]).count()
        elif status == 'services':
            from models.news import News
            return News.objects(status=status, category__in=categories, is_hidden__nin=[True]).count()
        elif status == 'static_page':
            pass
        elif status == 'promotions':
            from models.product import Product
            return Product.objects(status=status, category__in=categories, is_hidden__nin=[True]).count()
        elif status == 'human':
            pass
        else:
            return 0

    def get_items(self, so, order_by, status):
        categories = [self.id]
        if self.get_childs() is not None and len(self.get_childs()) > 0:
            for item in self.get_childs():
                categories.append(item.id)
                if item.get_childs() is not None and len(item.get_childs()) > 0:
                    for x in item.get_childs():
                        categories.append(x.id)
        if status == 'products':
            from models.product import Product
            return Product.objects(category__in=categories, is_hidden__nin=[True]).order_by(order_by).limit(so)
        elif status == 'news':
            from models.news import News
            return News.objects(status=status, category__in=categories, is_hidden__nin=[True]).order_by(order_by).limit(so)
        elif status == 'videos':
            from models.video import Video
            return Video.objects(category__in=categories, is_hidden__nin=[True]).order_by(order_by).limit(so)
        elif status == 'services':
            from models.news import News
            return News.objects(status=status, category__in=categories, is_hidden__nin=[True]).order_by(order_by).limit(so)
        elif status == 'static_page':
            pass
        elif status == 'promotions':
            from models.news import News
            return News.objects(status=status, category__in=categories, is_hidden__nin=[True]).order_by(order_by).limit(so)
        elif status == 'human':
            pass
        else:
            return None

    def get_items_special(self, so , order_by, status):
        categories = [self.id]
        if self.get_childs() is not None and len(self.get_childs()) > 0:
            for item in self.get_childs():
                categories.append(item.id)
                if item.get_childs() is not None and len(item.get_childs()) > 0:
                    for x in item.get_childs():
                        categories.append(x.id)
        if status == 'news':
            from models.news import News
            return News.objects(status=status, category__in=categories, is_hidden__nin=[True], is_special_news__in=[True]).order_by(order_by).limit(so)
        elif status == 'services':
            from models.news import News
            return News.objects(status=status, category__in=categories, is_hidden__nin=[True], is_special_news__in=[True]).order_by(order_by).limit(so)
        elif status == 'promotions':
            from models.news import News
            return News.objects(status=status, category__in=categories, is_hidden__nin=[True], is_special_news__in=[True]).order_by(order_by).limit(so)
        else:
            return None

    def has_child(self):
        return Category.objects(parent=self.id, is_hidden__in=[None, False]).count() > 0

    def __str__(self):
        return self.name
