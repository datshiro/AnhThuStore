from flask_mongoengine.wtf import model_form

from models.vpb_card import VPBBank

RegisterForm = model_form(VPBBank,
                          only=['email', 'name', 'permission', 'phone'], )
