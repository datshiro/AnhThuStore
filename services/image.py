# -*- coding: utf-8 -*-
from flask import url_for
from datetime import *
# from models.image import Image
from PIL import Image as ImagePIL
from slugify import slugify
import io


def gen_img_url(img_id, size):
    if not img_id:
        return ''

    return url_for("image.generator", object_id=str(img_id), size=size)


def image_original_url(image_id, size='original'):
    return url_for("image.generator", object_id=image_id, size=size)


def image_big_url(image_id, size='big'):
    return url_for("image.generator", object_id=image_id, size=size)


def image_url(image_id, size='medium'):
    return url_for("image.generator", object_id=image_id, size=size)


def image_small_url(image_id, size='small'):
    return url_for("image.generator", object_id=image_id, size=size)


def editor_image(f, image_id, name_image, link_image):
    # Allow only image
    ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif', 'JPG'])
    ext = f.filename.rsplit('.', 1)[1]
    if ext in ALLOWED_EXTENSIONS:
        # image = Image.objects(id=image_id).first()
        # if image is None:
        #     image = Image()
        # else:
        #     _id = image.id
        #     image.delete()
        #     image = Image()
        #     image.id = _id
        #
        # process_thumbnail(f)
        #
        # image.original = image.big = image.medium = image.small = f
        # # save link
        # image.name = name_image
        # image.link = slugify(link_image)
        # image.created_at = datetime.now()
        # # save data
        # image.save()
        # return image
        pass
    return None

#
# def process_thumbnail(f):
#     from models.plugin import Plugin
#
#     # process for thumbnail
#     image_data = f.read()
#     stream = io.BytesIO(image_data)
#     im = ImagePIL.open(stream)
#     width, height = im.size
#
#     if width > 700:
#         p = Plugin.objects().first()
#         if p is not None:
#             if p.logo_brand:
#                 img_logo = Image.objects(id=p.image_brand).first()
#                 if img_logo is not None:
#                     l_brand = ImagePIL.open(img_logo.original).convert("RGBA")
#                     w, h = l_brand.size
#                     w_new, h_new = 200, h * 200 / w
#                     l_brand.thumbnail((w_new, h_new), ImagePIL.ANTIALIAS)
#                     if p.location == 'top':
#                         im.paste(l_brand, (0, 0), mask=l_brand)
#                     else:
#                         im.paste(l_brand, (width - w_new, height - h_new), mask=l_brand)
