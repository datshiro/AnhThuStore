from flask_mongoengine.wtf import model_form

from models.vcb_card import VCBBank

RegisterForm = model_form(VCBBank,
                          only=['email', 'name', 'permission', 'phone'], )
