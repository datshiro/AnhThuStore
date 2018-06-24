# -*- coding: utf-8 -*-
from mongoengine import *

# from core.base_model import BaseModel
from services.image import gen_img_url


class NewsCategory(Document):
    name = StringField(required=True, max_length=255, verbose_name='Tên danh mục')
    description = StringField(verbose_name='Giới thiệu về danh mục')
    parent = ReferenceField('NewsCategory', reverse_delete_rule=NULLIFY, verbose_name='Các danh mục', null=True)
    image = StringField()
    banner = StringField()
    status = StringField(default='news')
    link = StringField(max_length=255, required=True, unique=True, verbose_name='Đường dẫn URL')
    no = IntField(required=True, default=0, verbose_name='Vị trí', max_length=255)
    is_hidden = BooleanField(default=False)
    is_special_category = BooleanField(default=False)
    meta_description = StringField(verbose_name='Mô tả SEO')
    meta_keywords = ListField(StringField(max_length=255), verbose_name='Mô tả SEO từ khóa')
    meta_title = StringField(verbose_name='Mô tả SEO tiêu đề', max_length=255)


    @classmethod
    def clean_data(cls, data):
        data['link'] = data['link'].encode('ascii', 'ignore').replace(' ', '-')
        data['meta_keywords'] = [i for i in data['meta_keywords'].split(',') if i != ''] if data['meta_keywords'] else []
        data['parent'] = NewsCategory.objects.get(id=data['parent']) if data['parent'] else ''
        return data


    @property
    def image_url(self):
        return gen_img_url(self.image, 'thumbnail')

    @property
    def image_original_url(self):
        return gen_img_url(self.image, 'original')

    @property
    def image_small_url(self):
        return gen_img_url(self.image, 'small')

    @property
    def image_banner_url(self):
        return gen_img_url(self.banner, 'thumbnail')

    @property
    def image_banner_original_url(self):
        return gen_img_url(self.banner, 'original')

    @property
    def image_banner_small_url(self):
        return gen_img_url(self.banner, 'small')

    def get_childs(self):
        return NewsCategory.objects(parent=self.id, is_hidden__ne=True).order_by('no')

    def get_childs_category_admin(self):
        return NewsCategory.objects(parent=self.id).order_by('no')

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
        if status == 'news':
            from models.news import News
            return News.objects(status=status, category__in=categories, is_hidden__nin=[True]).count()
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
        if status == 'news':
            from models.news import News
            return News.objects(status=status, category__in=categories, is_hidden__nin=[True]).order_by(order_by).limit(so)
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
        else:
            return None

    def has_child(self):
        return NewsCategory.objects(parent=self.id, is_hidden__in=[None, False]).count() > 0

    def __str__(self):
        return self.name


def list_status():
    return ['products', 'news', 'videos', 'services', 'promotions', 'static_page', 'human']


def validate_category_name(link, status):
    if link is None:
        raise ValidationError('link has exist in this category')
    category = NewsCategory.objects(link=link).first()
    if category is not None:
        link = link + '-' + status
        c = NewsCategory.objects(link=link).first()
        if c is not None:
            link = link + '-' + '1'
            s = NewsCategory.objects(link=link).first()
            return [False, link] if s is not None else [True, link]
        else:
            return [True, link]
    return [True, link]
