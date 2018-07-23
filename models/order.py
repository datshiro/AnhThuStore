import datetime

from mongoengine import *

def Order(Document):
    CASH_ON_STORE = 'cash_on_store'
    CASH_ON_DELIVERY = 'cash_on_delivery'
    PAYMENT_ONLINE = 'payment_online'
    BANK_TRANSFER = 'bank_transfer'

    PAYMENT_METHOD_CHOICES = (
        (CASH_ON_STORE, 'Trả tiền tại Cửa Hàng'),
        (CASH_ON_DELIVERY, 'Giao hàng (COD)'),
        (BANK_TRANSFER, 'Chuyển khoản online'),
        (PAYMENT_ONLINE, 'Thanh toán trực tuyến'),
    )

    PENDING = 'pending'
    CONFIRMED = 'confirmed'
    ON_DELIVERY = 'on_delivery'
    COMPLETE = 'complete'
    CANCELLED = 'cancelled'
    TRASH = 'trash'

    STATE_CHOICES = (
        (PENDING, 'Đang xử lý'),
        (CONFIRMED, 'Đã tiếp nhận'),
        (ON_DELIVERY, 'Đang giao hàng'),
        (COMPLETE, 'Hoàn thành'),
        (CANCELLED, 'Hủy'),
        (TRASH, 'Xóa(Rác)'),
    )

    uid = StringField(required=True, unique=True, max_length=255)
    state = StringField(default=PENDING, choices=STATE_CHOICES, verbose_name='Trạng thái')
    author = ReferenceField('User', reverse_delete_rule=NULLIFY)
    order_items = ListField(ReferenceField('OrderItem'))
    created_at = DateTimeField(default=datetime.datetime.now)
    success_at = DateTimeField()

    @property
    def total(self):
        total = 0
        for order_item in self.order_items:
            total += order_item.subtotal
        return total

    @property
    def humanized_state(self):
        return {
            'pending': 'Đang xử lý',
            'confirmed': 'Đã tiếp nhận',
            'on_delivery': 'Đang giao hàng',
            'complete': 'Hoàn thành',
            'cancelled': 'Hủy',
            'trash': 'Xóa(Rác)'
        }.get(self.state)