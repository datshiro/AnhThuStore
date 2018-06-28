from uuid import uuid4

from datetime import datetime
from mongoengine import UUIDField, ReferenceField, DateTimeField, BooleanField, DictField, Document

from models.user import User


class Session(Document):
    id = UUIDField(primary_key=True, default=uuid4)
    user = ReferenceField(User)
    data = DictField()
    updated_at = DateTimeField(default=datetime.utcnow)
    created_at = DateTimeField(default=datetime.utcnow)
    expired_at = DateTimeField()
    is_permanent = BooleanField()

    @property
    def is_authenticated(self):
        return bool(self.user)

    @property
    def is_anonymous(self):
        return not self.is_authenticated

    def set_data(self, key, value):
        self.data[key] = value
        self.save()

    def update_datetime(self):
        self.updated_at = datetime.utcnow()

    def __unicode__(self):
        return '<Session: {}>'.format(self.id)
