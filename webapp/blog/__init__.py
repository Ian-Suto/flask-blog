def create_module(app, **kwargs):
    """
    Register the Blog Blueprint with the Flask application.

    Args:
    - app (Flask): The Flask application.
    - **kwargs: Additional keyword arguments (if any).

    Returns:
    - None
    """
    from .controllers import blog_blueprint
    app.register_blueprint(blog_blueprint)