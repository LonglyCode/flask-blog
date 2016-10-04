#!usr/bin/env python
# -*- coding: utf-8 -*-

from flask import render_template,redirect,url_for
from . import main
from .forms import PostForm
from ..models import Permission,Post
from flask.ext.login import current_user
from app import db

# @main.route('/')
# def index():
#     return render_template('index.html')

@main.route('/',methods=['GET','POST'])
def index():
    form = PostForm()
    if current_user.can(Permission.WRITE_ARTICLES) and form.validate_on_submit():
        post= Post(body=form.body.data,author=current_user._get_current_object())
        db.session.add(post)
        return redirect(url_for('.index'))
    posts = Post.query.order_by(Post.timestamp.desc()).all()
    return render_template('index.html',form=form,posts=posts)
