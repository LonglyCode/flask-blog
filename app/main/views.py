# -*- coding: utf-8 -*-

from flask import render_template,redirect,url_for,abort,g,request
from . import main
from .forms import PostForm,SearchForm
from ..models import Permission,Post,Tag,Category
from flask_login import current_user
from app import db
from collections import defaultdict
from ..utils import keywords_split,pygments_style_defs

def change_tags(tags):
    l = []
    for tag in keywords_split(tags):
        tag_obj = Tag.query.filter_by(name=tag).first()
        if tag_obj is None:
            tag_obj=Tag(name=tag)
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
def index():
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
        return redirect(url_for('.index'))
    posts = Post.query.order_by(Post.pub_time.desc()).all()
    return render_template('index.html',form=form,posts=posts)


@main.route('/post/<int:id>',methods=['GET','POST'])
def post(id):
    post = Post.query.get_or_404(id)
    if not post.published:
        abort(403)
    return render_template('post.html',post=post)


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
        d[p.pub_time.year].append(p)
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
