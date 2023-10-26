from flask_login import UserMixin
from . import bcrypt
from .. import db, cache
from datetime import datetime
from ..blog.models import Post
from hashlib import sha256

roles = db.Table(
    'role_users',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer, db.ForeignKey('role.id'))
)

followers = db.Table(
    'followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)

class User(UserMixin, db.Model):
    """
    User model for managing user data.

    Attributes:
    - id (int): Primary key for the User model.
    - username (str): Unique and indexed field for the username.
    - password (str): Hashed password for the user.
    - about_me (str): Short description about the user.
    - last_seen (datetime): Timestamp for the user's last activity.
    - posts (relationship): A relationship to the Post model via a foreign key.
    - comments (relationship): A relationship to the Comment model via a foreign key.
    - roles (relationship): A relationship to the Role model through a many-to-many relationship.
    - followed (relationship): A relationship to other User objects, representing users that are followed by the current user.

    Methods:
    - __init__(self, username=''): Constructor for User objects.
    - avatar(self, size): Generate a Gravatar URL for the user's avatar.
    - has_role(self, name): Check if the user has a specific role.
    - set_password(self, password): Set and hash the user's password.
    - check_password(self, password): Check if a given password matches the user's hashed password.
    - follow(self, user): Follow another user.
    - unfollow(self, user): Unfollow a user.
    - is_following(self, user): Check if the user is following another user.
    - followed_posts(self): Retrieve posts of followed users.

    """
    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String(255), nullable=False, index=True, unique=True)
    password = db.Column(db.String(255))
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow())
    posts = db.relationship('Post', backref='user', lazy='dynamic')
    comments = db.relationship('Comment', backref='user', lazy='dynamic')

    roles = db.relationship(
        'Role',
        secondary=roles,
        backref=db.backref('users', lazy='dynamic')
    )

    followed = db.relationship(
        'User', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic'
    )

    def __init__(self, username=''):
        default = Role.query.filter_by(name='default').one()
        self.roles.append(default)
        self.username = username

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def avatar(self, size):
        digest = sha256(self.username.lower().encode('utf-8')).hexdigest()
        return "https://www.gravatar.com/avatar/{}?d=identicon&s={}".format(
            digest, size
        )
    
    
    @cache.memoize(60)
    def has_role(self, name):
        for role in self.roles:
            if role.name == name:
                return True
        return False
    
    def set_password(self, password):
        self.password = bcrypt.generate_password_hash(password)

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password, password)
    
    

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    def is_following(self, user):
        return self.followed.filter(
            followers.c.followed_id == user.id
        ).count() > 0

    def followed_posts(self):
        followed = Post.query.join(
            followers, (followers.c.followed_id == Post.user_id)).filter(
            followers.c.follower_id == self.id)
        own = Post.query.filter_by(user_id=self.id)
        return followed.union(own).order_by(Post.publish_date.desc())
        
class Role(db.Model):
    """
    Role model for managing user roles.

    Attributes:
    - id (int): Primary key for the Role model.
    - name (str): A unique name for the role.
    - description (str): A description of the role.

    Methods:
    - __init__(self, name): Constructor for Role objects.

    """
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<Role {}>'.format(self.name)