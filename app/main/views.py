# -*- coding: utf-8 -*-

from collections import defaultdict

from flask import (abort, current_app, g, redirect, render_template, request,
                   url_for)
from flask_login import current_user
from werkzeug.contrib.atom import AtomFeed, FeedEntry

from app import db

from . import main
from ..models import Category, Permission, Post, Tag
from ..utils import keywords_split, pygments_style_defs
from .forms import PostForm, SearchForm


def change_tags(tags):
    l = []
    for tag in keywords_split(tags):
        tag_obj = Tag.query.filter_by(name=tag).first()
        if tag_obj is None:
            tag_obj=Tag(name=tag)
            db.session.add(tag_obj)
            db.session.commit()
        l.append(tag_obj)
    return l


@main.before_app_request
def before_request():
    g.search_form = SearchForm()

@main.route('/search_results',methods=['GET','POST'])
def search_results(**kw):
    query=g.search_form.search.data
    results = Post.query.whoosh_search(query).all()
    return render_template('search.html',query=query,results=results)

@main.route('/pygments.css')
def pygments_css():
    return pygments_style_defs('monokai'),200,{'Content-Type':'text/css'}

@main.route('/',methods=['GET','POST'])
@main.route('/<int:page>',methods=['GET','POST'])
@main.route('/index/<int:page>',methods=['GET','POST'])
def index(page=1):
    form = PostForm()
    g.tags = Tag.query.all()
    g.categories = Category.query.all()
    if current_user.can(Permission.WRITE_ARTICLES) and form.validate_on_submit():
        post= Post(body=form.body.data,slug=form.data.slug,title=form.title.data,category=form.category.data,author=current_user._get_current_object())

        # add tags to post
        for t in change_tags(form.tags.data):
            if t:
                post.tags.append(t)

        db.session.add(post)
        return redirect(url_for('.index',page))
    posts = Post.query.order_by(Post.pub_time.desc()).paginate(page,current_app.config['POSTS_PER_PAGE'],False)
    return render_template('index.html',form=form,posts=posts)


@main.route('/post/<int:id>',methods=['GET','POST'])
def post(id):
    post = Post.query.get_or_404(id)
    if not post.published:
        abort(403)
    return render_template('page.html',post=post)


@main.route('/categories/<name>',methods=['GET','POST'])
def category(name):
    category = Category.query.filter_by(name=name).first()
    return render_template('result.html',item=category)


@main.route('/tags/<name>',methods=['GET','POST'])
def tag(name):
    tag = Tag.query.filter_by(name=name).first()
    return render_template('result.html',item=tag)


@main.route('/archives',methods=['GET','POST'])
def achieve_posts():
    posts = Post.query.all()
    d=defaultdict(list)
    for p in posts:
        d[str(p.pub_time.year)+"|"+str(p.pub_time.month)].append(p)
    return render_template('archives.html',d=d)


@main.route('/categories',methods=['GET','POST'])
def categories_posts():
    posts = Post.query.all()
    d=defaultdict(list)
    for p in posts:
        d[p.category].append(p)
    return render_template('categories.html',d=d)


@main.route('/tags',methods=['GET','POST'])
def tags_posts():
    tags = Tag.query.all()
    return render_template('tags.html',tags=tags)

@main.route('/feed/')
def feed():
    site_name = 'Lonely Code'

    feed = AtomFeed(
        "%s Recent" % site_name,
        feed_url=request.url,
        url=request.url_root,
    )

    posts = Post.query.order_by(Post.pub_time.desc()).limit(15).all()

    for post in posts:
        feed.add(post.title,
                 url=post.link,
                 content_type='html',
                 content=post.body_html,
                 updated=post.modified_time,
                 published=post.pub_time,
                 author=post.author.username,
                 summary=post.summary or '')
    return feed.get_response()
