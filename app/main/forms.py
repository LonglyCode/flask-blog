#!usr/bin/env python
# -*- coding: utf-8 -*-

from flask.ext.wtf import Form
from wtforms import StringField,SubmitField,TextAreaField,TextField
from wtforms.validators import Required
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from flask.ext.sqlalchemy import BaseQuery
from ..models import Category

class NameForm(Form):
    name = StringField('What is your name?', validators=[Required()])
    submit = SubmitField('Submit')

class PostForm(Form):
    title = StringField("add the title",validators=[Required()])
    slug = StringField("add the slug",validators=[Required()])
    tags = TextField("add the tag",validators=[Required()])
    category = QuerySelectField(u'选择分类',
                                query_factory=lambda:Category.query.all(),
                                get_pk = lambda r:r.id,
                                get_label = lambda r:r.name)
    body = TextAreaField("input your post content",validators=[Required()])
    submit = SubmitField(u'确定')

class SearchForm(Form):
    search = StringField('Search',validators=[Required()])
