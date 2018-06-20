# -*- coding: utf-8 -*-
# import xlrd
# import xlwt
import math
import io
from flask import request
from mongoengine import *
from slugify import slugify
from services.image import image_url, image_original_url, image_small_url


from services.excel_file import read_file_excel, get_image_list, get_id

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

    @classmethod
    def import_by_excel(cls, file_import):
        dloi = 0
        for i in read_file_excel(file_import):
            dloi += 1
            data = {}

            data['name'] = str(i[0]) if str(i[0]) is not None else ""

            if data['name'] is None:
                break

            data['link'] = str(i[1]) if str(i[0]) is not None else ""

            if data['link'] is None:
                data['link'] = slugify(data['name'])

            data['parent'] = get_id(str(i[2]), Category) if str(i[2]) is not None else None

            if data['parent'] is None or data['parent'] == '':
                del data['parent']

            data['is_hidden'] = True if str(i[3]) == '1' else False
            data['meta_title'] = str(i[4]) if str(i[4]) is not None else ""

            keywords_load = str(i[5]) if str(i[5]) is not None else ""
            keywords = []

            for x in keywords_load.split(','):
                if len(x) > 0 and x != '':
                    keywords.append(x)

            data['meta_description'] = str(i[6]) if str(i[6]) is not None else ""
            data['description'] = str(i[7]) if str(i[7]) is not None else ""
            data['image'] = get_image_list(str(i[8])) if str(i[8]) is not None else ""

            if data['image'] is not None and len(data['image']) >= 1:
                data['image'] = data['image'][0]
            else:
                del data['image']

            data['banner'] = get_image_list(str(i[9])) if str(i[9]) is not None else ""

            if data['banner'] is not None and len(data['banner']) >= 1:
                data['banner'] = data['banner'][0]
            else:
                del data['banner']

            data['no'] = float(i[10]) if float(i[10]) is not None else 0
            data['status'] = str(i[11]) if str(i[11]) is not None else "products"
            category = Category.objects(link=data['link']).first()

            if category is not None:
                update_map = dict([('set__' + key, value) for key, value in list(data.items())])
                category.update(**update_map)
                category.meta_keywords = keywords
                category.save()
            else:
                data['meta_keywords'] = keywords
                p = Category.objects.create(**data)

    # @classmethod
    # def export_excel(cls):
    #     font0 = xlwt.Font()
    #     font0.name = 'Times New Roman'
    #     font0.colour_index = 2
    #     font0.bold = True
    #     style0 = xlwt.XFStyle()
    #     style0.font = font0
    #     workbook = xlwt.Workbook()
    #     subs = Category.objects()
    #
    #     pages = int(math.ceil(subs.count() / 2000.0))
    #     for page in range(pages):
    #         page = page + 1
    #         ws = workbook.add_sheet('Sheet ' + str(page) + ' category')
    #         ws.write(0, 0, 'Ten Category', style0)
    #         ws.write(0, 1, 'URL Link', style0)
    #         ws.write(0, 2, 'Danh Muc', style0)
    #         ws.write(0, 3, 'An or Hien', style0)
    #         ws.write(0, 4, 'Mo Ta SEO', style0)
    #         ws.write(0, 5, 'Tu Khoa', style0)
    #         ws.write(0, 6, 'Mo Ta SE0', style0)
    #         ws.write(0, 7, 'Mo ta Dai', style0)
    #         ws.write(0, 8, 'Image Chinh', style0)
    #         ws.write(0, 9, 'Banner Chinh', style0)
    #         ws.write(0, 10, 'Vi tri', style0)
    #         ws.write(0, 11, 'Loai', style0)
    #         for index, sub in enumerate(subs[(page - 1) * 2000:page * 2000]):
    #             ws.write(index + 1, 0, sub.name)
    #             ws.write(index + 1, 1, sub.link)
    #             ws.write(index + 1, 2, sub.parent.name if sub.parent is not None else '')
    #             ws.write(index + 1, 3, 1 if sub.is_hidden else 0)
    #             ws.write(index + 1, 4, sub.meta_title)
    #             ws.write(index + 1, 5, [i + ',' for i in sub.meta_keywords] if sub.meta_keywords is not None else '')
    #             ws.write(index + 1, 6, sub.meta_description)
    #             ws.write(index + 1, 7, sub.description)
    #             ws.write(index + 1, 8, '{}/image/{}/original'.format(request.host, str(sub.image)))
    #             ws.write(index + 1, 9, '{}/image/{}/original'.format(request.host, str(sub.banner)))
    #             ws.write(index + 1, 10, sub.no)
    #             ws.write(index + 1, 11, sub.status)
    #     output = io.StringIO()
    #     workbook.save(output)
    #
    #     return output
