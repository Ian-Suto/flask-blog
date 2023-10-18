from flask_admin import Admin
from .. import db
from .controllers import CustomModelView, CustomView
from webapp.blog.models import Post, Comment, Tag
from webapp.auth.models import User, Role
import os.path as op

admin = Admin()

def create_module(app, **kwargs):
    admin.init_app(app)
    admin.add_view(CustomView(name='Custom'))

    models = [User, Role, Comment, Tag, Post]


    for model in models:
        admin.add_view(CustomModelView(model, db.session, category='Models'))
    