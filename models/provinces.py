# -*- coding: utf-8 -*-
from mongoengine import *
from slugify import slugify

from core.base_model import BaseModel
from models.plugin import Plugin
from models.districts import Districts


class Provinces(BaseModel):
    provinceid = StringField()
    name = StringField()
    type_value = StringField()

    @property
    def slug(self):
        return slugify(self.name, max_length=300)

    @property
    def url(self):
        from models.contact import Contact
        try:
            plugin = Plugin.objects().get()
            mapid = plugin.googleMapId
            if mapid is None:
                return ""
            contact = Contact.objects(provinceid=self.provinceid).limit(1)
            lll = contact[0].maping.split(',');
            ll = lll[1] + ',' + lll[0]
            return "https://www.google.com/maps/d/embed?mid="+mapid+"&hl=vi&msa=0&ie=UTF8&t=m&ll="+ll+"&spn=0.323714,0.439453&z=9&output=embed"
        except Exception as e:
            print(e)
            pass
        return ""

    @property
    def get_districts(self):
        return Districts.objects(provinceid=self.provinceid)

    def __str__(self):
        return self.name
