from datetime import datetime
from flask import (render_template, flash, redirect, url_for, request, g, jsonify, current_app)  # g for storing arbitrary attributes
from flask_babel import (_, get_locale)
from flask_login import (current_user, login_required)
from guess_language import guess_language
from app import db
from app.blog.forms import BlogPostForm
from app.main.forms import PostForm
from app.models import BlogPost, Post, role_required


from app.blog import bp
import urllib


@bp.route('/post', methods=['GET', 'POST'])
@login_required
@role_required('admin', 'user')
def blog_post():
    form = BlogPostForm()

    if form.validate_on_submit():
        if form.submit.data:
            language = guess_language(form.content.data)
            if language == 'UNKNOWN' or len(language) > 5:
                language = ''
            print('current user is:',current_user)
            post = BlogPost(title=form.title.data,
                            slug=form.slug.data,
                            content=form.content.data,
                            blog_author=current_user,
                            language=language)
            print(post)
            db.session.add(post)
            db.session.commit()
            flash(_('Your blog post is now live!'))
            return redirect(url_for('blog.blog'))
        elif form.preview.data:
            return render_template('blog/blog_post.html',
                                   title='Blog Posts',
                                   form=form,
                                   preview=True,
                                   blog_post=form.data
                                   )


    #page = request.args.get('page', 1, type=int)
    #posts = current_user.followed_posts().paginate(
    #    page, current_app.config['POSTS_PER_PAGE'], False)
    #next_url = url_for('main.index', page=posts.next_num) \
    #    if posts.has_next else None
    #prev_url = url_for('main.index', page=posts.prev_num) \
    #    if posts.has_prev else None

    return render_template('blog/blog_post.html',
                           title='Blog Posts',
                           form=form)

@bp.route('/', methods=['GET', 'POST'])
@login_required
def blog():
    page = request.args.get('page', 1, type=int)
    posts = BlogPost.query.order_by(BlogPost.timestamp.desc()).paginate(
        page, current_app.config['BLOG_POSTS_PER_PAGE'], False)
    next_url = url_for('blog.blog', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('blog.blog', page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('blog/blog.html',
                           title='Blog',
                           posts=posts.items,
                           next_url=next_url,
                           prev_url=prev_url)


@bp.route('/<slug>', methods=['GET', 'POST'])
@login_required
def show_blog_post(slug):
    blog_post = BlogPost.query.filter_by(slug=slug).first()
    page = request.args.get('page', 1, type=int)
    comments = Post.query.filter_by(blogpost_id=blog_post.id).order_by(Post.timestamp.desc()).paginate(
            page, current_app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('blog.show_blog_post', page=comments.next_num, slug=slug) \
        if comments.has_next else None
    prev_url = url_for('blog.show_blog_post', page=comments.prev_num, slug=slug) \
        if comments.has_prev else None

    form = PostForm()
    if form.validate_on_submit():
        language = guess_language(form.post.data)
        if language == 'UNKNOWN' or len(language) > 5:
            language = ''
        post = Post(body=form.post.data,
                    author=current_user,
                    language=language,
                    blogpost_id=blog_post.id)
        db.session.add(post)
        db.session.commit()
        flash(_('Your blog post has been added.'))
        return redirect(url_for('blog.show_blog_post', slug=slug))

    return render_template('blog/show_blog_post.html',
                           blog_post=blog_post,
                           posts=comments.items,
                           form=form,
                           next_url=next_url,
                           prev_url=prev_url
                           )

