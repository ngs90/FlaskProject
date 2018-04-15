from flask_wtf import FlaskForm
from wtforms import (StringField, SubmitField, TextAreaField)
from wtforms.validators import (ValidationError, DataRequired, Email, Length)
from app.models import User
from flask_login import current_user
from flask_babel import lazy_gettext as _l
from flask import request

class EditProfileForm(FlaskForm):
    username = StringField(_l('Username'), validators=[DataRequired()])
    email = StringField(_l('Email'), validators=[DataRequired(),Email()])
    about_me = TextAreaField(_l('About me'), validators=[Length(min=0,max=140)])
    submit = SubmitField(_l('Submit'))

    def validate_username(self, username): #names that starts with validate_<field_name> are invoked as additional validators by the WTForms
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            if hasattr(user, 'username'):
                if user.username != current_user.username:
                    raise ValidationError('Please use a different username.')


    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            if hasattr(user, 'email'):
                if user.email != current_user.email:
                    raise ValidationError('Please use a different email address.')

class PostForm(FlaskForm):
    post = TextAreaField(_l('Say something'), validators=[
        DataRequired(), Length(min=1, max=140)])
    submit = SubmitField('Submit')

class SearchForm(FlaskForm):
    q = StringField(_l('Search'), validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        if 'formdata' not in kwargs:
            kwargs['formdata'] = request.args
        if 'csrf_enabled' not in kwargs:
            kwargs['csrf_enabled'] = False
        super(SearchForm, self).__init__(*args, **kwargs)
