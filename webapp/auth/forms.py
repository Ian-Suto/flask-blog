from flask_wtf import FlaskForm
from flask_wtf.recaptcha import RecaptchaField
from wtforms import StringField, PasswordField, BooleanField,SubmitField
from wtforms.validators import DataRequired, Length, EqualTo, URL
from .models import User
from flask_babel import lazy_gettext as _l

class LoginForm(FlaskForm):
    username = StringField(_l('Username'), [DataRequired(), Length(max=255)])
    password = PasswordField(_l('Password'), [DataRequired()])
    submit = SubmitField(_l('Sign In'))
    remember = BooleanField(_l('Remember Me'))

    def validate(self, extra_validators=None):
        check_validate = super(LoginForm, self).validate()

        if not check_validate:
            return False
        
        user = User.query.filter_by(username=self.username.data).first()
        if not user:
            self.username.errors.append(_l('Invalid username or password'))
            return False
        
        if not user.check_password(self.password.data):
            self.username.errors.append(_l('Invalid username or password'))
            return False
        return True

class OpenIDForm(FlaskForm):
    openid = StringField('OpenID URL', [DataRequired(), URL()])

class RegisterForm(FlaskForm):
    username = StringField(_l('Username'), [DataRequired(), Length(max=255)])
    password = PasswordField(_l('Password'), [DataRequired(), Length(min=8)])
    confirm = PasswordField(_l('Confirm Password'), [DataRequired(), EqualTo('password')])
    recaptcha = RecaptchaField()

    def validate(self):
        check_validate = super(RegisterForm, self).validate()

        if not check_validate:
            return False
        
        user = User.query.filter_by(username=self.username.data).first()

        if user:
            self.username.errors.append(_l('User with name already exists'))
            return False
        
        return True

class EditProfileForm(FlaskForm):
    username = StringField(_l('Username'), [DataRequired()])
    about_me = StringField(_l('About me'), [Length(min=0, max=140)])
    sumbmit = SubmitField(_l('Submit'))

    def validate(self):
        check_validate = super(EditProfileForm, self).validate()

        if not check_validate:
            return False
        
        user = User.query.filter_by(username=self.username.data).first()

        if user:
            self.username.errors.append(_l('User with name already exists'))
            return False
        
        return True

class EmptyForm(FlaskForm):
    submit = SubmitField(_l('Submit'))