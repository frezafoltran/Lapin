from flask import request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, BooleanField, IntegerField, SelectField
from wtforms.validators import ValidationError, DataRequired, Length
from flask_babel import _, lazy_gettext as _l
from app.models import User
#from markupsafe import Markup


class EditProfileForm(FlaskForm):
    username = StringField(_l('Username'), validators=[DataRequired()])
    about_me = TextAreaField(_l('About me'), validators=[Length(min=0, max=140)])
    submit = SubmitField(_l('Submit'))

    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()

            if user is not None:
                raise ValidationError(_('This username is already being used. Please use a different one.'))


class PostForm(FlaskForm):
    post = TextAreaField(_l('Share an Idea'), validators=[DataRequired(), Length(min=1, max=140)])
    submit = SubmitField(_l('Submit'))


class SearchForm(FlaskForm):
    q = StringField(_l('Search'), validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        if 'formdata' not in kwargs:
            kwargs['formdata'] = request.args
        if 'csrf_enabled' not in kwargs:
            kwargs['csrf_enabled'] = False
        super(SearchForm, self).__init__(*args, **kwargs)


class URLfyForm(FlaskForm):
    word = StringField('', validators=[DataRequired()])
    submit = SubmitField(_l('Get URL'))


# question 4.1
class GraphPathForm(FlaskForm):
    choices = [('Angela', 'Angela'), ('Joao', 'Joao'), ('Elvira', 'Elvira'),
               ('Ringo', 'Ringo'), ('Pedro','Pedro'),
               ('Carol', 'Carol'), ('Sofia', 'Sofia'), ('Jude', 'Jude')]
    p1 = SelectField('Select first person', choices=choices, validators=[DataRequired()])

    choices = [('Ringo', 'Ringo'), ('Joao', 'Joao'), ('Elvira', 'Elvira'),
               ('Angela', 'Angela'), ('Pedro','Pedro'),
               ('Carol', 'Carol'), ('Sofia', 'Sofia'), ('Jude', 'Jude')]
    p2 = SelectField('Select second person', choices=choices, validators=[DataRequired()])
    curr_graph = StringField('')
    submit = SubmitField('Check if there\'s path')
