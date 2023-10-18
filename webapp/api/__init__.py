from flask_restful import Api
from .blog.controllers import PostApi, CommentApi

rest_api = Api()

def create_module(app, **kwargs):

    rest_api.add_resource(
        PostApi,
        '/api/post',
        '/api/post/<int:post_id>'
    )
    rest_api.add_resource(
        CommentApi,
        '/api/comment',
        '/api/comment/<int:comment_id>',
        '/api/post/<int:post_id>/comments',
    )
    rest_api.init_app(app)