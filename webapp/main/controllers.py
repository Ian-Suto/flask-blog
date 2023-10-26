from flask import Blueprint, redirect, url_for, render_template

main_blueprint = Blueprint('main', __name__, template_folder='../templates/main')

@main_blueprint.route('/')
def index():
    """
    Redirect to the 'blog.home' route.

    This route function redirects the user to the 'blog.home' route, which is
    typically the main landing page of the application.

    Returns:
    - Redirects the user to the 'blog.home' route.
    """
    return redirect(url_for('blog.home'))