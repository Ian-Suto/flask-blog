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
from . import oid, authenticate
from .models import db, User
from .forms import LoginForm, RegisterForm, OpenIDForm, EditProfileForm, EmptyForm
from flask_babel import _
from flask_login import login_required, current_user

auth_blueprint = Blueprint(
    'auth',
    __name__,
    template_folder='../templates/auth',
    url_prefix='/auth'
)
@auth_blueprint.route('/api', methods=['POST'])
def api():
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
@oid.loginhandler
def login():
    form = LoginForm()
    openid_form = OpenIDForm()

    if openid_form.validate_on_submit():
        return oid.try_login(
            openid_form.openid.data,
            ask_for=['nickname', 'email'],
            ask_for_optional=['fullname']
        )
    
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).one()
        login_user(user,  remember=form.remember.data)
        flash(_('You have been logged in.'), category='success')
        return redirect(url_for('main.index'))
    
    openid_errors = oid.fetch_error()
    if openid_errors:
        flash(openid_errors, category='danger')

    return render_template('login.html', form=form, openid_form=openid_form)

@auth_blueprint.route('/logout', methods=['GET', 'POST'])
def logout():
    logout_user()
    flash(_('You have been logged out.'), category='success')
    return redirect(url_for('main.index'))

@auth_blueprint.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash(_('Your changes have been saved.'))
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', form=form)

@auth_blueprint.route('/follow/<username>', methods=['POST'])
@login_required
def follow(username):
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
        flash(_('You are following %{username}!', username=username))
        return redirect(url_for('user', username=username))
    else:
        return redirect(url_for('index'))
    
@auth_blueprint.route('/unfollow/<username>', methods=['POST'])
@login_required
def unfollow(username):
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
        return redirect(url_for('user', username=username))
    else:
        return redirect(url_for('index'))



@auth_blueprint.route('/register', methods=['GET', 'POST'])
@oid.loginhandler
def register():
    form = RegisterForm()
    openid_form = OpenIDForm()

    if openid_form.validate_on_submit():
        return oid.try_login(
            openid_form.openid.data,
            ask_for=['nickname', 'email'],
            ask_for_optional=['fullname']
        )
    
    if form.validate_on_submit():
        new_user = User(form.username.data)
        new_user.set_password(form.password.data)

        db.session.add(new_user)
        db.session.commit()

        flash(_('Registration successful'), category='success')
        return redirect(url_for('.login'))
    
    openid_errors = oid.fetch_error()
    if openid_errors:
        flash(openid_errors, category='danger')

    return render_template('register.html', form=form, openid_form=openid_form)