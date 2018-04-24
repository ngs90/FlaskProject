from datetime import datetime
from app import (db, login)
from flask import current_app
from werkzeug.security import (generate_password_hash, check_password_hash)
from flask_login import UserMixin, current_user
from hashlib import md5
from time import time
import jwt
from app.search import add_to_index, remove_from_index, query_index
from functools import wraps

class SearchableMixin(object):
    @classmethod
    def search(cls, expression, page, per_page):
        ids, total = query_index(cls.__tablename__, expression, page, per_page)
        if total == 0:
            return cls.query.filter_by(id=0), 0
        when = []
        for i in range(len(ids)):
            when.append((ids[i], i))
        return cls.query.filter(cls.id.in_(ids)).order_by(
            db.case(when, value=cls.id)), total

    @classmethod
    def before_commit(cls, session):
        session._changes = {
            'add': [obj for obj in session.new if isinstance(obj, cls)],
            'update': [obj for obj in session.dirty if isinstance(obj, cls)],
            'delete': [obj for obj in session.deleted if isinstance(obj, cls)]
        }

    @classmethod
    def after_commit(cls, session):
        for obj in session._changes['add']:
            add_to_index(cls.__tablename__, obj)
        for obj in session._changes['update']:
            add_to_index(cls.__tablename__, obj)
        for obj in session._changes['delete']:
            remove_from_index(cls.__tablename__, obj)
        session._changes = None

    @classmethod
    def reindex(cls):
        for obj in cls.query:
            add_to_index(cls.__tablename__, obj)


followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)


def role_required(*role_args):
    def wrapper(f):
        @wraps(f)
        def decorated_view(*args,**kwargs):
            print('Checking user roles')
            role = [str(x) for x in current_user.get_role()]
            for role_arg in role_args:
                if str(role_arg) not in role:
                    return current_app.login_manager.unauthorized()
            return f(*args, **kwargs)
        return decorated_view
    return wrapper

class Role(db.Model):
    __tablename__ = 'role'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(50), unique=True)

    def __repr__(self):
        #return '<Role {}>'.format(self.name)
        return self.name



class UserRole(db.Model):
    __tablename__ = 'user_role'
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id', ondelete='CASCADE'))
    role_id = db.Column(db.Integer(), db.ForeignKey('role.id', ondelete='CASCADE'))


class User(UserMixin, db.Model):
    __table_args__ = {'extend_existing': True}  # Didn't work witout this, could be error with package:  https://stackoverflow.com/questions/27812250/sqlalchemy-inheritance-not-working and https://github.com/mitsuhiko/flask-sqlalchemy/issues/478
    id = db.Column(db.Integer, index=True, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    blog_posts = db.relationship('BlogPost', backref='blog_author', lazy='dynamic')
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    role = db.relationship('Role', secondary='user_role')

    followed = db.relationship(
        'User', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=retro&s={}'.format(
            digest, size)

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    def is_following(self, user):
        return self.followed.filter(
            followers.c.followed_id == user.id).count() > 0

    def followed_posts(self):
        followed = Post.query.join(
            followers, (followers.c.followed_id == Post.user_id)).filter(
            followers.c.follower_id == self.id)
        own = Post.query.filter_by(user_id=self.id)
        return followed.union(own).order_by(Post.timestamp.desc())

    def get_role(self):
        return self.role


    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            current_app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, current_app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class BlogPost(db.Model):
    __searchable__ = ['content']
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250))
    slug = db.Column(db.String(250))
    content = db.Column(db.String(250))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # Foreign key in the user table.
    blog_comment = db.relationship('Post', backref='blog_post', lazy='dynamic') #NOTICE! that the class-tabel BlogPost in the Foreign key statement is referred to as blog_post, i.e. capital letters after first is convert to _lowercase and initial letter is converted to lowercase (without the underscore)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    published = db.Column(db.Boolean, default=True)
    language = db.Column(db.String(5))

    def __repr__(self):
        return '<BlogPost {}>'.format(self.content)


class Post(SearchableMixin, db.Model):
    __searchable__ = ['body']
    __table_args__ = {'extend_existing': True}  # Didn't work witout this, could be error with package:  https://stackoverflow.com/questions/27812250/sqlalchemy-inheritance-not-working and https://github.com/mitsuhiko/flask-sqlalchemy/issues/478
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))  # Foreign key in the user table.
    blogpost_id = db.Column(db.Integer, db.ForeignKey('blog_post.id'))  # Foreign key in the user table.
    language = db.Column(db.String(5))

    def __repr__(self):
        return '<Post {}>'.format(self.body)

db.event.listen(db.session, 'before_commit', Post.before_commit)
db.event.listen(db.session, 'after_commit', Post.after_commit)

#db.event.listen(db.session, 'before_commit', BlogPost.before_commit)
#db.event.listen(db.session, 'after_commit', BlogPost.after_commit)


if __name__ == '__main__':
    u = User(username='lala', email='lala@example.com')
    print(u)

