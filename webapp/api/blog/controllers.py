import datetime
from email.policy import strict

from flask import abort, current_app, jsonify, request
from flask_restful import Resource, fields, marshal_with, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from webapp.blog.models import db, Post, Tag, Comment
from webapp.auth.models import User
from .parsers import (
    post_get_parser,
    post_post_parser,
    post_put_parser,
    comment_get_parser,
    comment_post_parser,
    comment_put_parser
)
from .fields import HTMLField

nested_tag_fields = {
    'id': fields.Integer(),
    'title': fields.String(),
}

post_fields = {
    'id': fields.Integer(),
    'user_id': fields.Integer(),
    'title': fields.String(),
    'text': HTMLField(),
    'tags': fields.List(fields.Nested(nested_tag_fields)),
    'publish_date': fields.DateTime(dt_format='iso8601')
}
comment_fields = {
    'id': fields.Integer(),
    'post_id': fields.Integer(),
    'user_id': fields.Integer(),
    'name': fields.String(),
    'text': HTMLField(),
    'date': fields.DateTime(dt_format='iso8601')
}
def add_tags_to_post(post, tags_list):
    for item in tags_list:
        tag = Tag.query.filter_by(title=item).first()

        if tag:
            post.tags.append(tag)
        else:
            new_tag = Tag(item)
            post.tags.append(new_tag)

class PostApi(Resource):
    @marshal_with(post_fields)
    @jwt_required()
    def get(self, post_id=None):
        """
        Get a post by its ID or a list of posts.

        Args:
            post_id (int): The ID of the post to retrieve. Defaults to None.

        Returns:
            Post or list of Post: The requested post(s).

        Raises:
            404: If the post with the given ID is non-existent.

        400: If 'page' or 'user' args are invalid.

        401: If authentication is required.

        403: If trying to edit a post not created by the current user.
        """
        if post_id:
            post = Post.query.get(post_id)
            if not post:
                abort(404, message="Post id is non-existent")
            return post
        else:
            args = post_get_parser.parse_args()
            page = args['page'] or 1

            if args['user']:
                user = User.query.filter_by(username=args['user']).first()
                if not user:
                    abort(404, message="Username not found...")
                
                posts = user.posts.order_by(
                    Post.publish_date.desc()
                ).paginate(page=args['page'] or 1,per_page=current_app.config.get('POSTS_PER_PAGE', 10),error_out=False)
            else:
                posts = Post.query.order_by(
                    Post.publish_date.desc()
                ).paginate(page=args['page'] or 1,per_page=current_app.config.get('POSTS_PER_PAGE', 10),error_out=False)

            return posts.items
    
    @jwt_required()
    def post(self):
        """
        Create a new post.

        Returns:
            dict: A dictionary containing the ID of the newly created post.

        Raises:
            400: If the request is missing required arguments.

            401: If authentication is required.
        """
        args = post_post_parser.parse_args(strict=True)
        new_post = Post(args['title'])
        new_post.user_id = get_jwt_identity()
        new_post.text = args['text']
        new_post.publish_date = datetime.datetime.now()

        if args['tags']:
            add_tags_to_post(new_post, args['tags'])

        db.session.add(new_post)
        db.session.commit()
        return {'id': new_post.id}, 201
    
    @jwt_required()
    def put(self, post_id=None):
        """
        Update an existing post.

        Args:
            post_id (int): The ID of the post to update. Defaults to None.

        Returns:
            dict: A dictionary containing the ID of the updated post.

        Raises:
            400: If the 'post_id' is not provided.

            401: If authentication is required.

            403: If trying to edit a post not created by the current user.
        """
        if not post_id:
            abort(400, message="Post id required...")
        post = Post.query.get(post_id)
        if not post:
            abort(404, message="Post non-existent...")
        args = post_put_parser.parse_args(strict=True)
        if get_jwt_identity() != post.user_id:
            abort(403,message="Can't edit post you didn't create")
        if args['title']:
            post.title = args['title']
        if args['text']:
            post.text = args['text']
        if args['tags']:
            add_tags_to_post(post, args['tags'])

        db.session.merge(post)
        db.session.commit()
        return {'id': post.id}, 201
    
    @jwt_required()
    def delete(self, post_id=None):
        """
        Delete an existing post.

        Args:
            post_id (int): The ID of the post to delete. Defaults to None.

        Returns:
            str: An empty string.

        Raises:
            400: If the 'post_id' is not provided.

            401: If authentication is required.

            404: If the post with the given ID is non-existent.

            403: If trying to delete a post not created by the current user.
        """
        if not post_id:
            abort(400, message="Post id required...")
        post = Post.query.get(post_id)
        if not post:
            abort(404, message="Post non-existent...")
        if get_jwt_identity() != post.user_id:
            abort(401, message="Authentication required...")

        db.session.delete(post)
        db.session.commit()
        return "", 204
    
class CommentApi(Resource):
    @marshal_with(comment_fields)
    @jwt_required()
    def get(self, comment_id=None, post_id=None):
        """
        Get a comment by its ID, a list of comments, or comments for a specific post or user.

        Args:
            comment_id (int): The ID of the comment to retrieve. Defaults to None.
            post_id (int): The ID of the post to retrieve comments for. Defaults to None.

        Returns:
            Comment or list of Comment: The requested comment(s).

        Raises:
            400: If 'page' or 'user' args are invalid.

            401: If authentication is required.

            403: If trying to edit a comment not created by the current user.
        """
        if comment_id:
            comment = Comment.query.get(comment_id)
            if not comment:
                abort(404, message="Comment id non-exixtent")
                print(f"comment: {comment}")
            return comment
        if post_id:
            post = Post.query.get(post_id)
            if not post:
                abort(404, message='Post not found ...')
            comments = post.comments.order_by(
                Comment.date.desc()
            )
            return comments
            
        else:
            args = comment_get_parser.parse_args()
            page = args['page'] or 1

            if args['user']:
                user = User.query.filter_by(username=args['user']).first()

                if not user:
                    abort(404, message='User not found...')
                comments = user.comments.order_by(
                    Comment.date.desc()
                ).paginate(page=args['page'] or 1, per_page=10, error_out=False)
            else:
                comments = Comment.query.order_by(
                    Comment.date.desc()
                ).paginate(page=args['page'] or 1, per_page=10, error_out=False)
            return comments.items
    
    @jwt_required()
    def post(self, post_id=None):
        """
        Create a new comment for a specific post.

        Args:
            post_id (int): The ID of the post to add a comment to. Defaults to None.

        Returns:
            dict: A dictionary containing the ID of the newly created comment.

        Raises:
            400: If the 'post_id' is not provided or if the request is missing required arguments.

            401: If authentication is required.
        """
        if not post_id:
            abort(400, message="Post id required...")
        post = Post.query.get(post_id)
        if not post:
            abort(404, message="Post non-existent...")
        args = comment_post_parser.parse_args(strict=True)
        new_comment = Comment()
        new_comment.text = args['text']
        new_comment.name = args['name']
        new_comment.user_id = get_jwt_identity()
        new_comment.post_id = post.id
        new_comment.date = datetime.datetime.now()

        db.session.add(new_comment)
        db.session.commit()
        return {'id': new_comment.id}, 201

    @jwt_required()
    def put(self, comment_id=None):
        """
        Update an existing comment.

        Args:
            comment_id (int): The ID of the comment to update. Defaults to None.

        Returns:
            dict: A dictionary containing the ID of the updated comment.

        Raises:
            400: If the 'comment_id' is not provided.

            401: If authentication is required.

            403: If trying to edit a comment not created by the current user.
        """
        if not comment_id:
            abort(400, message="Comment id required...")
        comment = Comment.query.get(comment_id)
        if not comment:
            abort(404, message="Comment non-existent...")
        args = comment_put_parser.parse_args()
        if get_jwt_identity() != comment.user_id:
            abort(403, message="Can't edit comment you didn't create")
        #if args['name']:
            #comment.name = args['name']
        if args['text']:
            comment.text = args['text']
        
        db.session.merge(comment)
        db.session.commit()
        return {'id': comment.id}, 201
    
    @jwt_required()
    def delete(self, comment_id=None):
        """
        Delete an existing comment.

        Args:
            comment_id (int): The ID of the comment to delete. Defaults to None.

        Returns:
            str: An empty string.

        Raises:
            400: If the 'comment_id' is not provided.

            401: If authentication is required.

            404: If the comment with the given ID is non-existent.

            403: If trying to delete a comment not created by the current user.
        """
        if not comment_id:
            abort(400, message='Comment id required...')
        comment = Comment.query.get(comment_id)
        if not comment:
            abort(404, message='Comment non-exixtent...')
        if get_jwt_identity() != comment.user_id:
            abort(403, message="Can't delete comment you didn't create")
        
        db.session.delete(comment)
        db.session.commit()
        return "", 204