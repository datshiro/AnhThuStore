from mongoengine import *


class Map(Document):
    name = StringField(required=True)
    coordinates = StringField(required=True)
    description = StringField()
