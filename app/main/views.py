# -*- coding: utf-8 -*-

from flask import render_template,redirect,url_for,abort
from . import main
from .forms import PostForm
from ..models import Permission,Post,Tag,Category
from flask.ext.login import current_user
from app import db
from collections import defaultdict
from ..utils import keywords_split

def change_tags(tags):
    l = []
    for tag in keywords_split(tags):
        tag_obj = Tag.query.filter_by(name=tag).first()
        if tag_obj is None:
            tag_obj=Tag(name=tag)
        l.append(tag_obj)
    return l

@main.route('/',methods=['GET','POST'])
def index():
    form = PostForm()
    if current_user.can(Permission.WRITE_ARTICLES) and form.validate_on_submit():
        post= Post(body=form.body.data,slug=form.data.slug,title=form.title.data,category=form.category.data,author=current_user._get_current_object())

        # add tags to post
        for t in change_tags(form.tags.data):
            if t:
                post.tags.append(t)

        db.session.add(post)
        return redirect(url_for('.index'))
    posts = Post.query.order_by(Post.pub_time.desc()).all()
    return render_template('index.html',form=form,posts=posts)

@main.route('/post/<int:id>')
def post(id):
    post = Post.query.get_or_404(id)
    if not post.published:
        abort(403)
    return render_template('post.html',posts=[post])


@main.route('/categories/<slug>')
def category(slug):
    category = Category.query.get_or_404(slug)
    return render_template('post.html',categories=[category])


@main.route('/archives')
def achieve_posts():
    posts = Post.query.all()
    d=defaultdict(list)
    for p in posts:
        d[p.pub_time.year].append(p)
    return render_template('archives.html',d=d)
