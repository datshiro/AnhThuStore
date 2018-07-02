from flask_mongoengine.wtf import model_form

from models.user import User

UserForm = model_form(User,
                      exclude=['created_at', 'updated_at', 'permission', 'user_type', 'group'],
                      field_args={'password': {'password': True}}
                      )