from flask import Flask
from flask_bootstrap import Bootstrap4
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import MetaData
from flask_debugtoolbar import DebugToolbarExtension
from dotenv import load_dotenv
from flask_caching import Cache
from flask_moment import Moment

convention = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(column_0_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}
db = SQLAlchemy(metadata=MetaData(naming_convention=convention), )
migrate = Migrate()
debug_toolbar = DebugToolbarExtension()
cache = Cache()
moment = Moment()

def create_app(object_name):
    load_dotenv()
    app = Flask(__name__)
    app.config.from_object(object_name)
    bootstrap = Bootstrap4(app)
    cache.init_app(app)

    db.init_app(app)
    migrate.init_app(app, db, render_as_batch=True)
    debug_toolbar.init_app(app)
    moment.init_app(app)


    from .auth import create_module as auth_create_module
    from .blog import create_module as blog_create_module
    from .main import create_module as main_create_module
    from .api import create_module as api_create_module
    from .admin import create_module as admin_create_module
    from .babel import create_module as babel_create_module

    auth_create_module(app)
    blog_create_module(app)
    main_create_module(app)
    api_create_module(app)
    admin_create_module(app)
    babel_create_module(app)
    return app