from app import db
from wtforms import (StringField, SubmitField, TextAreaField, BooleanField)
from wtforms.validators import (DataRequired)
from flask_babel import lazy_gettext as _l
from wtforms_alchemy import Unique
import re
from app.models import BlogPost
from flask_wtf import FlaskForm
from flask_pagedown.fields import PageDownField

class BlogPostForm(FlaskForm):
    title = StringField(_l('Title'), validators=[DataRequired()])  # , Unique(BlogPost.title)
    slug = StringField(_l('Slug'), validators=[DataRequired()])  # , Unique(BlogPost.slug)
    #content = TextAreaField(_l('Blog post'), validators=[DataRequired()]) #markdown format
    content = PageDownField(_l('Blog post'),
                            validators=[DataRequired()],
                            render_kw={"rows": 12}) #markdown supported
    published = BooleanField(_l('Publish?'))
    submit = SubmitField(_l('Submit'))
    preview = SubmitField(_l('Preview (with equations)'))

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = re.sub('[^\w]+', '-', self.title.lower())
        ret = super(BlogPost, self).save(*args, **kwargs)
        return ret




