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