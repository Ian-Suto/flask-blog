import logging
import click
from faker import Faker
from .auth import bcrypt
from .blog.models import Tag, Post, Comment
from .auth.models import User, Role, db
import random

log = logging.getLogger(__name__)

faker = Faker()

fake_users = [
    {'username': 'user_default', 'role': 'default'},
    {'username': 'user_poster', 'role': 'poster'},
    {'username': 'admin', 'role': 'admin'}
]

fake_roles = ['default', 'poster', 'admin']

def generate_tags(n):
    """
    Generate a list of tags with random names.

    Args:
        n (int): The number of tags to generate.

    Returns:
        list: A list of Tag objects.

    This function generates a list of tags with random names and stores them in the database.
    """
    tags = list()
    for i in range(n):
        tag_title = faker.color_name()
        tag = Tag.query.filter_by(title=tag_title).first()
        if tag:
            tags.append(tag)
            continue
        tag = Tag()
        tag.title = tag_title
        tags.append(tag)
        try:
            db.session.add(tag)
            db.session.commit()
        except Exception as e:
            log.error("Failed to add tag %s: %s" % (str(tag), e))
            db.session.rollback()
    return tags

def generate_roles():
    """
    Generate roles from a predefined list of role names.

    Returns:
        list: A list of Role objects.

    This function generates Role objects from a predefined list of role names and stores them in the database.
    """
    roles = list()
    for rolename in fake_roles:
        role = Role.query.filter_by(name=rolename).first()
        if role:
            roles.append(role)
            continue
        role = Role(rolename)
        roles.append(role)

        try:
            db.session.add(role)
            db.session.commit()
        except Exception as e:
            log.error("Error inserting role: %s, %s" % (str(role), e))
            db.session.rollback()
    return roles

def generate_users():
    users = list()
    for item in fake_users:
        user = User.query.filter_by(username=item['username']).first()
        if user:
            users.append(user)
            continue
        user = User()
        poster = Role.query.filter_by(name=item['role']).one_or_none()
        if poster is None:
            log.warning("Role not found: %s" % item['role'])
            continue
        user.roles.append(poster)
        user.username = item['username']
        user.password = bcrypt.generate_password_hash("password")
        users.append(user)
        try:
            db.session.add(user)
            db.session.commit()
        except Exception as e:
            log.error("Error inserting user: %s, %s" % (str(user), e))
            db.session.rollback()
    return users

def generate_posts(n, users, tags):
    posts = list()
    for i in range(n):
        post = Post()
        post.title = faker.sentence()
        post.text = faker.text(max_nb_chars=1000)
        post.publish_date = faker.date_this_decade(before_today=True, after_today=False)
        post.user_id = users[random.randrange(0, len(users))].id
        post.tags = [tags[random.randrange(0, len(tags))] for i in range(0, 2)]


        posts.append(post)
        try:
            db.session.add(post)
            db.session.commit()
        except Exception as e:
            log.error("Fail to add post %s: %s" % (str(post), e))
            db.session.rollback()
    return posts

def generate_comments(users, posts):
    for post in posts:
        num_comments = random.randint(1, 5)
        for i in range(num_comments):

            comment = Comment()
            comment.name = users[random.randrange(0, len(users))].username
            comment.text = faker.sentence()
            comment.date = faker.date_this_decade(before_today=True, after_today=False)
            comment.post_id = posts[random.randrange(0, 100)].id
            try:
                db.session.add(comment)
                db.session.commit()
            except Exception as e:
                log.error('Failed to add comment %s: %s' % (str(comment), e))
                db.session.rollback()


def register(app):
    """
    Register custom command-line commands for the Flask application.

    Args:
        app: The Flask application.

    This function registers custom command-line commands using Flask's CLI interface.
    """

    @app.cli.command('test-data')
    def test_data():
        """
        Generate test data for roles, users, posts, tags, and comments.

        This command generates test data for roles, users, posts, tags, and comments and inserts it into the database.
        """
        generate_roles()
        users = generate_users()
        tags = generate_tags(5)
        posts = generate_posts(100, users, tags)
        generate_comments(users, posts)

    @app.cli.command('create_user')
    @click.argument('username')
    @click.argument('password')
    def create_user(username, password):
        user = User()
        user.username = username
        user.password = password
        try:
            db.session.add(user)
            db.session.commit()
            click.echo('User {0} Added.'.format(username))
        except Exception as e:
            log.error('Fail to add new user: %s Error: %s' % (username, e))
            db.session.rollback()

    @app.cli.command('create-admin')
    @click.argument('username')
    @click.argument('password')
    def create_admin(username, password):
        admin_role = Role.query.filter_by(name='admin').scalar()
        user = User()
        user.username = username
        user.set_password(password)
        user.roles.append(admin_role)
        try:
            db.session.add(user)
            db.session.commit()
            click.echo('User {0} Added.'.format(username))
        except Exception as e:
            log.error("Fail to add new user: %s Error: %s" % (username, e))
            db.session.rollback()

    @app.cli.command('list-users')
    def list_users():
        try:
            users = User.query.all()
            for user in users:
                click.echo('{0}'.format(user.username))
        except Exception as e:
            log.error("Fail to list users Error: %s" % e)
            db.session.rollback()
    
    @app.cli.command('list-routes')
    def list_routes():
        for url in app.url_map.iter_rules():
            click.echo("%s %s %s" % (url.rule, url.methods, url.endpoint))