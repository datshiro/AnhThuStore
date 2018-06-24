# -*- coding: utf-8 -*-
from mongoengine import *
from datetime import *

# from core.base_model import BaseModel
from models.image import Image
# from services.image import image_url, image_original_url, image_small_url
from slugify import slugify
import urllib.request, urllib.error, urllib.parse
import xmltodict
from services.time_ago import pretty_date
from models.news_category import NewsCategory


class News(Document):

    NEWS = 'news'
    SERVICES = 'services'
    PROMOTIONS = 'promotions'

    STATUS_CHOICES = (
        (NEWS, 'News'),
        (SERVICES, 'Services'),
        (PROMOTIONS, 'Promotions'),
    )

    name = StringField(verbose_name='Tiêu đề bài viết', required=True, max_length=255)
    image = StringField()
    images = ListField(ReferenceField('Image', reverse_delete_rule=NULLIFY))
    video = StringField(verbose_name='URL hoặc ID Youtube', max_length=255)
    link = StringField(verbose_name='Đường Dẫn URL', required=True, unique=True, max_length=255)
    description = StringField(verbose_name='Nội dung bài viết')
    short_description = StringField(verbose_name='Mô tả ngắn', max_length=500)
    author = ReferenceField('User', required=True, reverse_delete_rule=NULLIFY)
    category = ListField(ReferenceField('NewsCategory', reverse_delete_rule=NULLIFY), verbose_name='Danh Mục Tin')
    view = IntField(default=0)
    is_hidden = BooleanField(default=False)
    is_landing_page = BooleanField(default=False)
    landing_page = StringField()
    status = StringField(default=NEWS, choices=STATUS_CHOICES, verbose_name='Loại bài viết')
    next_post = ObjectIdField()
    prev_post = ObjectIdField()
    created_at = DateTimeField(required=True, default=datetime.now)
    updated_at = DateTimeField(required=True, default=datetime.now)
    publish_at = DateTimeField(verbose_name='Đăng Vào Lúc', required=True, default=datetime.now)
    is_special_news = BooleanField(default=False)
    meta_description = StringField(verbose_name='Mô tả SEO')
    meta_keywords = ListField(StringField(max_length=255), verbose_name='Mô tả SEO từ khóa')
    meta_title = StringField(verbose_name='Mô tả SEO tiêu đề', max_length=255)

    FORM_FIELD = [
        'status',
        'name',
        'short_description',
        'description',
        'publish_at',
        'link',
        'video',
        'category',
        'meta_title',
        'meta_keywords',
        'meta_description',
        'image'
    ]

    # @property
    # def image_url(self):
    #     if self.image is None or len(self.image) == 0:
    #         return ""
    #     return image_url(self.image)
    #
    # @property
    # def image_original_url(self):
    #     if self.image is None or len(self.image) == 0:
    #         return ""
    #     return image_original_url(self.image)
    #
    # @property
    # def image_small_url(self):
    #     if self.image is None or len(self.image) == 0:
    #         return ""
    #     return image_small_url(self.image)

    def get_time_remain_s(self):
        time = self.publish_at - datetime.now()
        _total = time.days*24*3600 + time.seconds
        return _total

    def get_time(self):
        return str(self.created_at.day) + "/" + str(self.created_at.month) + "/" + str(self.created_at.year)

    def get_time_ago(self):
        time = self.created_at
        return pretty_date(time=time)

    def get_time_publish_ago(self):
        time = self.publish_at
        return pretty_date(time=time)

    def con_ngay_pub(self):
        temp = self.publish_at - datetime.now()
        return str(temp.days) + 'Day ' + fm(temp.seconds/3600) + ':' + fm(temp.seconds%3600/60) + ":" + fm(temp.seconds%3600%60)

    def get_new(self, so, order_by):
        news = News.objects(publish_at__lte=datetime.now(), id__nin=[self.id], is_hidden__nin=[True], category__in=self.category, status=self.status).order_by(order_by).limit(so)
        return news

    def get_like_comment_count(self, url):
        like = 0
        comment = 0
        url = "https://api.facebook.com/restserver.php?method=links.getStats&urls=" + \
            str(url)
        try:
            file = urllib.request.urlopen(url)
            data = file.read()
            file.close()
            data = xmltodict.parse(data)
            note = data.get('links_getStats_response')
            like = note.get('link_stat').get('like_count')
            comment = note.get('link_stat').get('comment_count')
        except Exception as e:
            pass
        return {'like': like, 'comment': comment}


    @property
    def link_next(self):
        return News.objects(id=self.next_post).first() if self.next_post is not None else None

    @property
    def link_prev(self):
        return News.objects(id=self.prev_post).first() if self.prev_post is not None else None

    @classmethod
    def get_last_visibles(cls, limit=10):
        return cls.objects(is_hidden__ne=True).order_by('-created_at').limit(limit)

    @classmethod
    def get_visibles(cls):
        return cls.objects(is_hidden__ne=True).order_by('-created_at')[:10]

    def __str__(self):
        return self.name

    def delete(self, signal_kwargs=None, **write_concern):
        self.process_next_prev_delete()
        super(News, self).delete()

    def process_next_prev_delete(self):
        if self.next_post is not None:
            next_post = News.objects(category=self.category, id=self.next_post).first()
            if next_post is not None:
                next_post.prev_post = self.prev_post
                next_post.save()
        if self.prev_post is not None:
            prev_post = News.objects(category=self.category, id=self.prev_post).first()
            if prev_post is not None:
                prev_post.next_post = self.next_post
                prev_post.save()


def list_status():
    return ['news', 'services', 'promotions']


def fm(x):
    return '{0:02d}'.format(x)
