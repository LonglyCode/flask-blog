#!usr/bin/env python
# -*- coding: utf-8 -*-

from flask import render_template,redirect,url_for
from . import main
from .forms import PostForm
from ..models import Permission,Post,Tag
from flask.ext.login import current_user
from app import db

def chang_tags(tags):
    l = []
    for tag in tags:
        tag_obj = Tag.query.filter_by(name=tag).first()
        if tag_obj is None:
            tag_obj=Tag(name=tag)
        l.append(tag_obj)
    return l

@main.route('/',methods=['GET','POST'])
def index():
    form = PostForm()
    if current_user.can(Permission.WRITE_ARTICLES) and form.validate_on_submit():
        post= Post(body=form.body.data,title=form.title.data,category=form.category.data,tags=chang_tags(form.tags.data),author=current_user._get_current_object())
        db.session.add(post)
        return redirect(url_for('.index'))
    posts = Post.query.order_by(Post.pub_time.desc()).all()
    return render_template('index.html',form=form,posts=posts)

@main.route('/post/<int:id>')
def post(id):
    post = Post.query.get_or_404(id)
    return render_template('post.html',posts=[post])
