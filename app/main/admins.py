# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from flask import flash, redirect, url_for, request
from flask_login import current_user, login_required
from app import admin, db
from flask_admin import expose
from ..models import Post, User, Category, Tag
from ..decorators import admin_required
from flask_admin.contrib.sqla import ModelView
from flask_admin.contrib.fileadmin import FileAdmin
from datetime import datetime
from flask_admin import Admin
from app.utils import markdown_render
from app.utils import pygmented_markdown


class PostAdmin(ModelView):

    column_list = ('title','category','pub_time','published')
    column_searchable_list = ('title',)
    column_editable_list = ('title','slug')
    column_filters = ('category',)

    column_labels = dict(
        title=('标题'),
        slug=('URL Slug'),
        category=('类别'),
        body=('正文'),
        summary=('摘要'),
        published=('发布'),
        pub_time=('创建时间'),
    )

    can_create = True
    can_edit = True
    can_delete = True

    def is_accessible(self):
        return current_user.is_administrator()

    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        return redirect(url_for('main.index', next=request.url))

    # Model handlers
    def on_model_change(self, form, model, is_created):
        if is_created:
            model.author_id = current_user.id
            model.pub_time = datetime.now()
            model.modified_time = model.pub_time
            model.body_html = markdown_render(model.body)
        else:
            model.modified_time = datetime.now()

class UserAdmin(ModelView):

    column_list = ('email','username','role','confirmed')
    column_searchable_list = ('username','email')
    column_filters = ('role',)

    column_labels = dict(
        email=('邮箱'),
        username=('用户名'),
        confirmed=('已确认'),
        role=('角色'),
    )

    can_create = True
    can_edit = True
    can_delete = True

    def is_accessible(self):
        return current_user.is_administrator()

    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        return redirect(url_for('main.index', next=request.url))

class CategoryAdmin(ModelView):

    column_list = ('slug','name',)
    column_searchable_list = ('name',)

    can_create = True
    can_edit = True
    can_delete = True

    def is_accessible(self):
        return current_user.is_administrator()

    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        return redirect(url_for('main.index', next=request.url))

    column_labels = dict(
        name=('名字'),
        slug=('URL SLUG'),
    )

class TagAdmin(ModelView):

    column_list = ('name',)
    column_searchable_list = ('name',)

    can_create = True
    can_edit = True
    can_delete = True

    def is_accessible(self):
        return current_user.is_administrator()

    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        return redirect(url_for('main.index', next=request.url))

class MyFileAdmin(FileAdmin):

    def is_accessible(self):
        return current_user.is_administrator()

    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        return redirect(url_for('main.index', next=request.url))

import os.path as op
path = op.join(op.dirname(__file__), '../static')
admin.add_view(PostAdmin(Post, db.session, name='文章'))
admin.add_view(CategoryAdmin(Category, db.session, name='分类'))
admin.add_view(UserAdmin(User, db.session, name='用户'))
admin.add_view(TagAdmin(Tag, db.session, name='标签'))
admin.add_view(MyFileAdmin(path,'/static/',name='文件'))
