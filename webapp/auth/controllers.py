import datetime
from urllib import request
from flask import (render_template,
                   Blueprint,
                   redirect,
                   url_for,
                   flash,
                   request,
                   jsonify)
from flask_login import login_user, logout_user
from flask_jwt_extended import create_access_token
from . import authenticate
from .models import db, User
from .forms import LoginForm, RegisterForm,EditProfileForm, EmptyForm
from flask_babel import _
from flask_login import login_required, current_user

auth_blueprint = Blueprint(
    'auth',
    __name__,
    template_folder='../templates/auth',
    url_prefix='/auth'
)

@auth_blueprint.before_request
def before_request():
    """
    Execute actions before handling a request.

    This function updates the user's last_seen timestamp.

    Returns:
    - None
    """
    if current_user.is_authenticated:
        current_user.last_seen = datetime.datetime.utcnow()

@auth_blueprint.route('/api', methods=['POST'])
def api():
    """
    API endpoint for user authentication.

    Receives a JSON request containing username and password.
    If authentication is successful, it returns an access token.

    Returns:
    - 400 if JSON is missing.
    - 400 if username or password is missing.
    - 401 if the username or password is incorrect.
    - 200 with an access token if authentication is successful.
    """
    if not request.is_json:
        return jsonify({'msg': 'Missing JSON in request'}), 400
    
    username = request.json.get('username', None)
    password = request.json.get('password', None)
    if not username:
        return jsonify({'msg':'Missing username parameter'}), 400
    if not password:
        return jsonify({'msg':'Missing password parameter'}), 400
    user = authenticate(username, password)
    if not user:
        return jsonify({"msg":"Bad username or password"}), 401
    
    access_token = create_access_token(identity=user.id)
    return jsonify(access_token=access_token), 200

@auth_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    """
    Login view with login form.

    Allows users to log in with a valid username and password.
    Redirects to the home page if login is successful.

    Returns:
    - GET: Render the login form.
    - POST: Redirect to the home page on successful login, or show login form again on failure.
    """
    form = LoginForm()
    
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).one()
        login_user(user,  remember=form.remember.data)
        flash(_('You have been logged in.'), category='success')
        return redirect(url_for('main.index'))

    return render_template('login.html', form=form)

@auth_blueprint.route('/logout', methods=['GET', 'POST'])
def logout():
    """
    Logout view.

    Logs the user out and redirects to the home page.

    Returns:
    - Redirects to the home page with a logout message.
    """
    logout_user()
    flash(_('You have been logged out.'), category='success')
    return redirect(url_for('main.index'))

@auth_blueprint.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    """
    Edit user profile view.

    Allows logged-in users to edit their profile information.

    Returns:
    - GET: Render the profile edit form.
    - POST: Save changes and redirect to the profile edit form on success or show validation errors on failure.
    """
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash(_('Your changes have been saved.'))
        return redirect(url_for('auth.edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', form=form)

@auth_blueprint.route('/follow/<username>', methods=['POST'])
@login_required
def follow(username):
    """
    Follow another user view.

    Allows users to follow other users.
    Handles user following and redirects to the profile of the user being followed.

    Returns:
    - Redirects to the profile of the followed user.
    """
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()
        if user is None:
            flash(_('User %{username} not found.', username=username))
            return redirect(url_for('index'))
        if user == current_user:
            flash(_('You cannot follow yourself!'))
            return redirect(url_for('user', username=username))
        current_user.follow(user)
        db.session.commit()
        flash(_('You are following %(username)s!', username=username))
        return redirect(url_for('auth.profile', username=username))
    else:
        return redirect(url_for('index'))
    
@auth_blueprint.route('/unfollow/<username>', methods=['POST'])
@login_required
def unfollow(username):
    """
    Unfollow another user view.

    Allows users to unfollow other users.
    Handles user unfollowing and redirects to the profile of the user being unfollowed.

    Returns:
    - Redirects to the profile of the unfollowed user.
    """
    form = EmptyForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=username).first()
        if user is None:
            flash(_('User %{username} not found.', username=username))
            return redirect(url_for('index'))
        if user == current_user:
            flash(_('You cannot unfollow yourself!'))
            return redirect(url_for('user', username=username))
        current_user.follow(user)
        db.session.commit()
        flash(_('You are no longer following %{username}!', username=username))
        return redirect(url_for('auth.profile', username=username))
    else:
        return redirect(url_for('index'))

@auth_blueprint.route('/user_profiles')
@login_required
def user_profiles():
    """
    User profiles view.

    Displays a list of user profiles.

    Returns:
    - Renders a list of user profiles.
    """
    users = User.query.all()
    form = EmptyForm()
    return render_template('user_profiles.html', users=users, form=form)

@auth_blueprint.route('/register', methods=['GET', 'POST'])
def register():
    """
    User registration view.

    Allows new users to register an account.

    Returns:
    - GET: Render the registration form.
    - POST: Redirects to the login page on successful registration or shows validation errors on failure.
    """
    form = RegisterForm()
    if form.validate_on_submit():
        new_user = User(form.username.data)
        new_user.set_password(form.password.data)

        db.session.add(new_user)
        db.session.commit()

        flash(_('Registration successful'), category='success')
        return redirect(url_for('.login'))

    return render_template('register.html', form=form)