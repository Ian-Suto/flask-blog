from flask import Blueprint, session, redirect, url_for

babel_blueprint = Blueprint(
    'babel',
    __name__,
    url_prefix="/babel"
)

@babel_blueprint.route('/<string:locale>')
def index(locale):
    """
    Change the user's preferred locale and redirect to the home page.

    Args:
    - locale (str): The user's selected locale.

    Returns:
    - Redirects to the 'blog.home' route after updating the session's 'locale' variable.
    """
    session['locale'] = locale
    return redirect(url_for('blog.home'))