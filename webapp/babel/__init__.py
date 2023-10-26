from flask import has_request_context, session
from flask_babel import Babel

babel = Babel()


def get_locale():
    """
    Get the user's preferred locale based on the session.

    Returns:
    - str: The user's preferred locale (e.g., 'en' for English).
    """
    if has_request_context():
        locale = session.get('locale')
        if locale:
            return locale
        session['locale'] = 'en'
        return session['locale']

def create_module(app, **kwargs):
    """
    Initialize the Babel extension and register the Babel blueprint with the Flask app.

    Args:
    - app (Flask): The Flask application.
    - **kwargs: Additional keyword arguments (if any).

    Returns:
    - None
    """
    babel.init_app(app, locale_selector=get_locale)
    from .controllers import babel_blueprint
    app.register_blueprint(babel_blueprint)