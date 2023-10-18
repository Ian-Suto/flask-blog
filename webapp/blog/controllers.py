import datetime
from sqlalchemy import desc, func
from flask import render_template, Blueprint, flash, redirect, url_for, current_app, abort, request, get_flashed_messages, session, g
from flask_login import login_required, current_user
from .models import db, Post, Tag, Comment, tags

from .forms import CommentForm, PostForm
from ..auth.models import User
from ..auth import has_role
from .. import cache
from flask_babel import _, get_locale

blog_blueprint = Blueprint(
    'blog',
    __name__,
    template_folder='../templates/blog',
    url_prefix='/blog'
)
@blog_blueprint.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.datetime.utcnow()
    g.locale = str(get_locale())
def make_cache_key(*args, **kwargs):
    path = request.path
    args = str(hash(frozenset(request.args.items())))
    messages = str(hash(frozenset(get_flashed_messages())))
    if current_user.is_authenticated:
        roles = str(current_user.roles)
    else:
        roles=""
    return (path + args + roles + session.get('locale', '') + messages).encode('utf-8')

@cache.cached(timeout=7200, key_prefix="sidebar_data")
def sidebar_data():
    recent = Post.query.order_by(Post.publish_date.desc()).limit(5).all()
    # Using a joined load to get the posts with their associated tags
    posts_with_tags = Post.query.options(db.joinedload(Post.tags)).all()

    # Counting the occurrences of each tag
    tag_count = {}
    for post in posts_with_tags:
        for tag in post.tags:
            tag_count[tag] = tag_count.get(tag, 0) + 1

    # Getting the top tags based on the count
    top_tags = sorted(tag_count.items(), key=lambda x: x[1], reverse=True)[:5]
    return recent, top_tags

@blog_blueprint.route('/')
@blog_blueprint.route('/home')
@cache.cached(timeout=60)
def home():
    page = request.args.get('page',1, type=int)
    posts = Post.query.order_by(Post.publish_date.desc()).paginate(page=page,per_page=current_app.config.get('POSTS_PER_PAGE', 10),error_out=False)

    recent, top_tags = sidebar_data()

    return render_template('home.html', posts=posts, recent=recent, top_tags=top_tags)

@blog_blueprint.route('/followed_posts')
@login_required
@cache.cached(timeout=60)
def followed_posts():
    page = request.args.get('page', 1, type=int)
    posts = current_user.followed_posts().paginate(page=page,per_page=current_app.config.get('POSTS_PER_PAGE', 10),error_out=False)

    recent, top_tags = sidebar_data()

    return render_template('home.html', posts=posts, recent=recent, top_tags=top_tags)

@blog_blueprint.route('/new_post', methods=['GET', 'POST'])
@login_required
@has_role('poster')
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        new_post = Post()
        new_post.title = form.title.data
        new_post.user_id = current_user.id
        new_post.text = form.text.data
        new_post.publish_date = datetime.datetime.utcnow()
        db.session.add(new_post)
        db.session.commit()
        flash(_('Post added'), category='success')
        return redirect(url_for('.post', post_id=new_post.id))
    return render_template('new.html', form=form)

@blog_blueprint.route('/edit/<int:id>', methods=['GET','POST'])
@login_required
def edit_post(id):
    post = Post.query.get_or_404(id)
    #Current user can edit posts
    if current_user.id == post.user.id:
        form = PostForm()
        if form.validate_on_submit():
            post.title = form.title.data
            post.text = form.text.data
            post.publish_date = datetime.datetime.utcnow()
            db.session.merge(post)
            db.session.commit()
            return redirect(url_for('.post', post_id=post.id))
        form.title.data = post.title
        form.text.data = post.text
        return render_template('edit.html', form=form, post=post)
    abort(403)

@blog_blueprint.route('/post/<int:post_id>', methods=['GET', 'POST'])
@cache.cached(timeout=60, key_prefix=make_cache_key)
def post(post_id):
    form = CommentForm()

    if form.validate_on_submit():
        new_comment = Comment()
        new_comment.name = form.name.data
        new_comment.text = form.text.data
        new_comment.post_id = post_id
        new_comment.date = datetime.datetime.utcnow()
        try:
            db.session.add(new_comment)
            db.session.commit()
        except Exception as e:
            flash('Error adding your comment: %s' % str(e), category='error')
            db.session.rollback()
        else:
            flash(_('Comment added'), category='info')
        return redirect(url_for('blog.post', post_id=post_id))
    
    post = Post.query.get_or_404(post_id)
    tags = post.tags
    comments = post.comments.order_by(Comment.date.desc()).all()
    recent, top_tags = sidebar_data()

    return render_template(
        'post.html',
        post=post,
        tags=tags,
        comments=comments,
        recent=recent,
        top_tags=top_tags,
        form=form,
    )

@blog_blueprint.route('/tag/<string:tag_name>')
@cache.cached(timeout=60, key_prefix=make_cache_key)
def posts_by_tag(tag_name):
    tag = Tag.query.filter_by(title=tag_name).first_or_404()
    posts = tag.posts.order_by(Post.publish_date.desc()).all()
    recent, top_tags = sidebar_data()

    return render_template(
        'tag.html',
        tag=tag,
        posts=posts,
        recent=recent,
        top_tags=top_tags
    )

@blog_blueprint.route('/user/<string:username>')
@cache.cached(timeout=60, key_prefix=make_cache_key)
def posts_by_user(username):
    user = User.query.filter_by(username=username).first_or_404()
    posts = user.posts.order_by(Post.publish_date.desc()).all()
    recent, top_tags = sidebar_data()

    return render_template(
        'user.html',
        user=user,
        posts=posts,
        recent=recent,
        top_tags=top_tags
    )