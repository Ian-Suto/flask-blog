from .. import db
import datetime
from hashlib import sha256, md5
tags = db.Table(
    'post_tags',
    db.Column('post_id', db.Integer, db.ForeignKey('post.id')),
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'))
)

    
class Post(db.Model):
    """
    Represents a blog post.

    Attributes:
    - id (int): Unique identifier for the post.
    - title (str): Title of the post.
    - text (str): Content of the post.
    - publish_date (datetime): Date and time when the post was published.
    - user_id (int): ID of the user who created the post.
    - comments (relationship): Relationship to associated comments.
    - tags (relationship): Relationship to associated tags.

    Methods:
    - __init__(self, title=""): Initializes a new post with an optional title.
    - __repr__(self): Returns a string representation of the post.
    """
    id = db.Column(db.Integer(), primary_key=True)
    title = db.Column(db.String(255))
    text = db.Column(db.Text())
    publish_date = db.Column(db.DateTime())
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id'))
    comments = db.relationship('Comment', backref='post', lazy='dynamic')
    tags = db.relationship('Tag', secondary=tags, backref=db.backref('posts', lazy='dynamic'))

    def __init__(self, title=""):
        self.title = title

    def __repr__(self):
        return "<Post '{}'>".format(self.title)
    
class Comment(db.Model):
    """
    Represents a comment on a blog post.

    Attributes:
    - id (int): Unique identifier for the comment.
    - name (str): Name of the comment author.
    - text (str): Content of the comment.
    - date (datetime): Date and time when the comment was created.
    - post_id (int): ID of the post associated with the comment.
    - user_id (int): ID of the user who created the comment.

    Methods:
    - __repr__(self): Returns a string representation of the comment.
    - avatar(self, size): Generates a Gravatar URL for the comment author's avatar.
    """
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(255))
    text = db.Column(db.Text())
    date = db.Column(db.DateTime())
    post_id = db.Column(db.Integer(), db.ForeignKey('post.id'))
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id'))

    def __repr__(self):
        return "<Comment '{}'>".format(self.text[:15])
    
    def avatar(self, size):
        digest = sha256(self.name.lower().encode('utf-8')).hexdigest()
        return "https://www.gravatar.com/avatar/{}?d=identicon&s={}".format(
            digest, size
        )
    
class Tag(db.Model):
    """
    Represents a tag associated with blog posts.

    Attributes:
    - id (int): Unique identifier for the tag.
    - title (str): Title or name of the tag.

    Methods:
    - __init__(self, title=""): Initializes a new tag with an optional title.
    - __repr__(self): Returns a string representation of the tag.
    """
    id = db.Column(db.Integer(), primary_key=True)
    title = db.Column(db.String(255))

    def __init__(self, title=""):
        self.title = title

    def __repr__(self):
        return "<Tag '{}'>".format(self.title)