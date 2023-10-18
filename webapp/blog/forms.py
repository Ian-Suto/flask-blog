from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField
from wtforms.validators import InputRequired, Length
from flask_babel import lazy_gettext as _l

class CommentForm(FlaskForm):
    name = StringField(
        _l('Name'), [InputRequired(), Length(max=255)]
    )
    text = TextAreaField(_l('Comment'), [InputRequired()])

class PostForm(FlaskForm):
    title = StringField(
        _l('Title'),
        [InputRequired(), Length(max=255)]
    )
    text = TextAreaField(_l('Content'), [InputRequired()])