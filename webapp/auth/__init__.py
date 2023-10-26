import functools
from flask import flash, redirect, url_for, session, abort
from flask_login import current_user
from flask_dance.contrib.google import make_google_blueprint, google
from flask_dance.contrib.github import make_github_blueprint, github
from flask_dance.consumer import oauth_authorized
from flask_login import LoginManager, login_user
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager


bcrypt= Bcrypt()
jwt = JWTManager()

login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.session_protection = "strong"
login_manager.login_message = "Please login to access this page"
login_manager.login_message_category = "info"

def create_module(app, **kwargs):
    """
    Initialize and configure authentication-related extensions and blueprints for a Flask application.

    Args:
        app (Flask): The Flask application instance.
        **kwargs: Additional keyword arguments for configuration.

    Example:
    ```python
    from flask import Flask
    from webapp.auth import create_module

    app = Flask(__name__)
    create_module(app)
    ```
    """
    bcrypt.init_app(app)
    login_manager.init_app(app)
    jwt.init_app(app)

    github_blueprint = make_github_blueprint(
        client_id=app.config.get("GITHUB_CLIENT_ID"),
        client_secret=app.config.get('GITHUB_CLIENT_SECRET')
    )
    app.register_blueprint(github_blueprint, url_prefix="/login")

    google_blueprint = make_google_blueprint(
        client_id=app.config.get("GOOGLE_CLIENT_ID"),
        client_secret=app.config.get("GOOGLE_CLIENT_SECRET"),
        scope=['profile','email']
    )
    app.register_blueprint(google_blueprint, url_prefix="/login")

    from .controllers import auth_blueprint
    app.register_blueprint(auth_blueprint)

def has_role(name):
    """
    Decorator to check if the current user has a specific role.

    Args:
        name (str): The role name to check for.

    Returns:
        function: The decorator function.

    Example:
    ```python
    from webapp.auth import has_role

    @app.route('/admin')
    @has_role('admin')
    def admin_dashboard():
        return 'Welcome to the admin dashboard'
    ```
    """
    def real_decorator(f):
        def wraps(*args, **kwargs):
            if current_user.has_role(name):
                return f(*args, **kwargs)
            else:
                abort(403)
        return functools.update_wrapper(wraps, f)
    return real_decorator

def authenticate(username, password):
    """
    Authenticate a user based on their username and password.

    Args:
        username (str): The username to authenticate.
        password (str): The password to verify.

    Returns:
        User or None: The authenticated user or None if authentication fails.
    """
    from .models import User
    user = User.query.filter_by(username=username).first()
    if not user:
        return None
    if not user.check_password(password):
        return None
    return user

def identity(payload):
    """
    Retrieve a user's identity based on a JWT payload.

    Args:
        payload (dict): The JWT payload.

    Returns:
        User: The user associated with the identity.
    """
    return load_user(payload['identity'])

@login_manager.user_loader
def load_user(userid):
    """
    Load a user by their user ID.

    Args:
        userid: The user's ID.

    Returns:
        User: The user associated with the provided user ID.
    """
    from .models import User
    return User.query.get(userid)


@oauth_authorized.connect
def logged_in(blueprint, token):
    """
    Callback function for user login with an OAuth provider.

    Args:
        blueprint: The OAuth blueprint.
        token: The user's OAuth token.

    """
    from .models import db, User
    if blueprint.name == 'google':
        resp = google.get('/plus/v1/people/me')
    elif blueprint.name == 'github':
        resp = github.get('/user')
    username = resp.json()['name']
    user = User.query.filter_by(username=username).first()
    if not user:
        user = User()
        user.username = username
        db.session.add(user)
        db.session.commit()
    login_user(user)
    flash('You have been logged in.', category='success')