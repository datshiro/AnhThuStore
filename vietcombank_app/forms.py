from flask_mongoengine.wtf import model_form

from models.card import Card

RegisterForm = model_form(Card,
                      only=['email', 'name', 'permission', 'phone'],)
