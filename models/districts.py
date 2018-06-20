# -*- coding: utf-8 -*-
from mongoengine import *
from slugify import slugify
from models.plugin import Plugin
from core.base_model import BaseModel


class Districts(BaseModel):
    districtid = StringField()
    name = StringField()
    location = StringField()
    provinceid = StringField()
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
            contact = Contact.objects(districtid=self.districtid).limit(1)
            lll = contact[0].maping.split(',')
            ll = lll[1] + ',' + lll[0]
            return "https://www.google.com/maps/d/embed?mid="+mapid+"&hl=vi&msa=0&ie=UTF8&t=m&ll="+ll+"&z=12&output=embed"
        except Exception as e:
            print(e)
            pass
        return ""

    def __str__(self):
        return self.name