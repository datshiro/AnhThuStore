# -*- coding: utf-8-*-
from mongoengine import StringField, ListField
from flask_mongoengine import Document


class UserGroup(Document):
    name = StringField(required=True, unique=True, min_length=3)
    short_description = StringField(required=True, min_length=3)
    permissions = ListField(field=StringField())

    @staticmethod
    def get_permission_list(regroup=True):
        if not regroup:
            return permissions()

        res = {}
        for p in permissions():
            if p[3] not in res:
                res[p[3]] = []
            res[p[3]].append(p)
        return res

    def __str__(self):
        return self.name


def permissions():
    return [
        ("dashboard", "tachometer alternate", "Báo cáo tổng thể", "dashboard", True, 'Dashboard', 0),

        ("affiliate", "users", "Bán hàng liên kết", "affiliate", True, 'Dashboard', 0),

        ("crm", "group", "Liên kết tài khoản mạng xã hội", "source", True, 'User - Group', 3),

        ("user_group", "group", "Quản lí nhóm", "user_group", True, 'User - Group', 0),
        ("create_user_group", "group", "Thêm", "user_group", False, 'User - Group', 1),
        ("edit_user_group", "group", "Sửa", "user_group", False, 'User - Group', 2),
        ("delete_user_group", "group", "Xóa", "user_group", False, 'User - Group', 3),

        ("user", "user", "Thành Viên", "user", True, 'User - Group', 0),
        ("create_user", "user", "Thêm", "user", False, 'User - Group', 1),
        ("edit_user", "user", "Sửa", "user", False, 'User - Group', 2),
        ("delete_user", "user", "Xóa", "user", False, 'User - Group', 3),

        ("subscriber", "envelope", "Danh sách email", "subscriber", True, 'User - Group', 0),
        ("create_subscriber", "smile", "Thêm", "subscriber", False, 'User - Group', 1),
        ("edit_subscriber", "smile", "Sửa", "subscriber", False, 'User - Group', 2),
        ("delete_subscriber", "smile", "Xóa", "subscriber", False, 'User - Group', 3),

        ("customer", "dollar", "Khách hàng", "customer", True, 'User - Group', 0),
        ("create_customer", "flask", "Thêm", "customer", False, 'User - Group', 1),
        ("edit_customer", "flask", "Sửa", "customer", False, 'User - Group', 2),
        ("delete_customer", "flask", "Xóa", "customer", False, 'User - Group', 3),

        ("customer_card", "flask", "Customer card", "customer_card", True, 'User - Group', 0),
        ("create_customer_card", "flask", "Thêm", "customer_card", False, 'User - Group', 1),
        ("edit_customer_card", "flask", "Sửa", "customer_card", False, 'User - Group', 2),
        ("delete_customer_card", "flask", "Xóa", "customer_card", False, 'User - Group', 3),

        ("contact", "map marker", "Bản đồ từng Store", "contact", True, 'map', 0),
        ("create_contact", "map marker", "Thêm", "contact", False, 'map', 1),
        ("edit_contact", "map marker", "Sửa", "contact", False, 'map', 2),
        ("delete_contact", "map marker", "Xóa", "contact", False, 'map', 3),

        ("store", "home", "Cửa hàng", "store", True, 'map', 0),
        ("create_store", "flask", "Thêm", "store", False, 'map', 1),
        ("edit_store", "flask", "Sửa", "store", False, 'map', 2),
        ("delete_store", "flask", "Xóa", "store", False, 'map', 3),

        ("category", "folder open", "Nhóm sản phẩm", "category", True, 'Product', 0),
        ("create_category", "folder open", "Thêm", "category", False, 'Product', 1),
        ("edit_category", "folder open", "Sửa", "category", False, 'Product', 2),
        ("delete_category", "folder open", "Xóa", "category", False, 'Product', 3),

        ("giftcode", "gift", "Mã giảm giá", "giftcode", True, 'Product', 0),
        ("create_giftcode", "gift", "Thêm", "giftcode", False, 'Product', 1),
        ("edit_giftcode", "gift", "Sửa", "giftcode", False, 'Product', 2),
        ("delete_giftcode", "gift", "Xóa", "giftcode", False, 'Product', 3),

        ("product", "barcode", "Sản phẩm", "product", True, 'Product', 0),
        ("create_product", "barcode", "Thêm", "product", False, 'Product', 1),
        ("edit_product", "barcode", "Sửa", "product", False, 'Product', 2),
        ("delete_product", "barcode", "Xóa", "product", False, 'Product', 3),

        ("product_type", "puzzle", "Thuộc tính sản phẩm", "product_type", False, 'Product', 0),
        ("create_product_type", "puzzle", "Thêm", "product_type", False, 'Product', 1),
        ("edit_product_type", "puzzle", "Sửa", "product_type", False, 'Product', 2),
        ("delete_product_type", "puzzle", "Xóa", "product_type", False, 'Product', 3),

        ("product_type_detail", "puzzle", "Giá trị thuộc tính", "product_type_detail", False, 'Product', 0),
        ("create_product_type_detail", "puzzle", "Thêm", "product_type_detail", False, 'Product', 1),
        ("edit_product_type_detail", "puzzle", "Sửa", "product_type_detail", False, 'Product', 2),
        ("delete_product_type_detail", "puzzle", "Xóa", "product_type_detail", False, 'Product', 3),

        ("brand", "trademark", "Thương hiệu", "brand", True, 'Product', 0),
        ("create_brand", "trademark", "Thêm", "brand", False, 'Product', 1),
        ("edit_brand", "trademark", "Sửa", "brand", False, 'Product', 2),
        ("delete_brand", "trademark", "Xóa", "brand", False, 'Product', 3),

        ("menu", "sitemap", "Menu", "menu", True, 'Website', 0),
        ("create_menu", "sitemap", "Thêm", "menu", False, 'Website', 1),
        ("edit_menu", "sitemap", "Sửa", "menu", False, 'Website', 2),
        ("delete_menu", "sitemap", "Xóa", "menu", False, 'Website', 3),

        ("media", "image", "File hình ảnh", "interface", True, 'Website', 0),

        ("news", "file alternate", "Bài viết", "news", True, 'Website', 0),
        ("create_news", "file alternate", "Thêm", "news", False, 'Website', 1),
        ("edit_news", "file alternate", "Sửa", "news", False, 'Website', 2),
        ("delete_news", "file alternate", "Xóa", "news", False, 'Website', 3),

        ("news_category", "folder open", "Nhóm bài viết", "news_category", True, 'Website', 0),
        ("create_news_category", "folder open", "Thêm", "news_category", False, 'Website', 1),
        ("edit_news_category", "folder open", "Sửa", "news_category", False, 'Website', 2),
        ("delete_news_category", "folder open", "Xóa", "news_category", False, 'Website', 3),

        ("service", "bullhorn", "Dịch vụ", "service", True, 'Website', 0),
        ("create_service", "bullhorn", "Thêm", "service", False, 'Website', 1),
        ("edit_service", "bullhorn", "Sửa", "service", False, 'Website', 2),
        ("delete_service", "bullhorn", "Xóa", "service", False, 'Website', 3),

        ("promotion", "star", "Khuyến Mãi", "promotion", True, 'Website', 0),
        ("create_promotion", "star", "Thêm", "promotion", False, 'Website', 1),
        ("edit_promotion", "star", "Sửa", "promotion", False, 'Website', 2),
        ("delete_promotion", "star", "Xóa", "promotion", False, 'Website', 3),

        ("video", "film", "Video", "video", True, 'Website', 0),
        ("create_video", "film", "Thêm", "video", False, 'Website', 1),
        ("edit_video", "film", "Sửa", "video", False, 'Website', 2),
        ("delete_video", "film", "Xóa", "video", False, 'Website', 3),

        ("video_category", "folder open", "Danh mục Video", "video_category", True, 'Website', 0),
        ("create_video_category", "folder open", "Thêm", "video_category", False, 'Website', 1),
        ("edit_video_category", "folder open", "Sửa", "video_category", False, 'Website', 2),
        ("delete_video_category", "folder open", "Xóa", "video_category", False, 'Website', 3),

        ("slider", "sliders horizontal", "Quản lý slider", "slider", True, 'Website', 0),
        ("create_slider", "sliders horizontal", "Thêm", "slider", False, 'Website', 1),
        ("edit_slider", "sliders horizontal", "Sửa", "slider", False, 'Website', 2),
        ("delete_slider", "sliders horizontal", "Xóa", "slider", False, 'Website', 3),

        ("banner", "image", "Quản lý banner ảnh", "banner", True, 'Website', 0),
        ("create_banner", "image", "Thêm", "banner", False, 'Website', 1),
        ("edit_banner", "image", "Sửa", "banner", False, 'Website', 2),
        ("delete_banner", "image", "Xóa", "banner", False, 'Website', 3),

        ("static_page", "edit", "Tạo Trang - Landing Page", "static_page", True, 'Website', 0),
        ("create_static_page", "edit", "Thêm", "static_page", False, 'Website', 1),
        ("edit_static_page", "edit", "Sửa", "static_page", False, 'Website', 2),
        ("delete_static_page", "edit", "Xóa", "static_page", False, 'Website', 3),

        ("order", "usd", "Đơn hàng online", "order", True, 'Buy - Sell', 0),
        ("create_order", "usd", "Thêm", "order", False, 'Buy - Sell', 1),
        ("edit_order", "usd", "Sửa", "order", False, 'Buy - Sell', 2),
        ("delete_order", "usd", "Xóa", "order", False, 'Buy - Sell', 3),

        ("order_offline", "usd", "Đơn hàng POS", "order_offline", True, 'Buy - Sell', 0),
        ("create_order_offline", "usd", "Thêm", "order_offline", False, 'Buy - Sell', 1),
        ("edit_order_offline", "usd", "Sửa", "order_offline", False, 'Buy - Sell', 2),
        ("delete_order_offline", "usd", "Xóa", "order_offline", False, 'Buy - Sell', 3),

        ("cod", "truck", "Vận chuyển", "cod", True, 'map', 0),
        ("create_cod", "truck", "Thêm", "cod", False, 'map', 1),
        ("edit_cod", "truck", "Sửa", "cod", False, 'map', 2),
        ("delete_cod", "truck", "Xóa", "cod", False, 'map', 3),

        ("warehouse", "cube", "Kho hàng", "warehouse", True, 'map', 0),
        ("create_warehouse", "cube", "Thêm", "warehouse", False, 'map', 1),
        ("edit_warehouse", "cube", "Sửa", "warehouse", False, 'map', 2),
        ("delete_warehouse", "cube", "Xóa", "warehouse", False, 'map', 3),

        ("import_product", "cube", "Nhập kho", "import_product", True, 'map', 0),
        ("create_import_product", "cube", "Thêm", "import_product", False, 'map', 1),
        ("edit_import_product", "cube", "Sửa", "import_product", False, 'map', 2),
        ("delete_import_product", "cube", "Xóa", "import_product", False, 'map', 3),

        ("plugin", "cog", "Cài đặt Chung", "plugin", True, 'Configure', 0),
        ("create_plugin", "cog", "Thêm", "plugin", False, 'Configure', 1),
        ("edit_plugin", "cog", "Sửa", "plugin", False, 'Configure', 2),
        ("delete_plugin", "cog", "Xóa", "plugin", False, 'Configure', 3),

        ("interface", "tv", "Giao diện", "interface", True, 'Configure', 0),

        ("domain", "link", "Domain", "domain", True, 'Configure', 0),

        ("source", "code", "Source code", "source", True, 'Configure', 0),
        ("create_source", "group", "Thêm", "source", False, 'Configure', 1),
        ("edit_source", "group", "Sửa", "source", False, 'Configure', 2),
        ("delete_source", "group", "Xóa", "source", False, 'Configure', 3),
    ]
