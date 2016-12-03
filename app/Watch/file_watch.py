# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
from os.path import splitext,basename
from app import db
from ..models import Post,Tag,Category,User
from ..utils import keywords_split
import re
import codecs

__all__=['FileWatch']
pattern = re.compile(r'(?P<title>title.*\n)(?P<category>category.*\n)(?P<tags>tags.*\n)')
pattern_body = re.compile(r'<!-- toc -->',re.I)

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

class FileWatch(FileSystemEventHandler):

    def __init__(self,app=None):
        self._type = None
        self._path = None
        if app is not None:
            self.set_app(app)

    def set_app(self,app):
        self.app=app

    def on_any_event(self,event):
        self._path =event.src_path
        self._type = splitext(self._path)[1]

    def on_created(self,event):
        if self._type ==".md":
            with open(self._path) as f:
                string = f.read()
        elif self._type == ".html":
            print "add a new html file,%s"%self._path

    def on_deleted(self, event):
        if self._type ==".md":
            print "delete markdown file,%s"%self._path
        elif self._type == ".html":
            print "delete html file,%s"%self._path

    def on_modified(self, event):
        if self._type ==".md":
            with codecs.open(self._path,mode='rb',encoding="utf-8") as f:
                string = f.read()
            match=re.search(pattern,string)
            match_body=re.search(pattern_body,string)
            with self.app.app_context(): # must in app_context
                category =match.group('category').split(':')[1].strip()
                c = Category.query.filter_by(name=category).first()
                if c is None:
                    c = Category(slug="wu",name=category)
                    db.session.add(c)

                t =match.group('title').split(':')[1].strip()
                u = User.query.get(1) # default user name
                body_start = match_body.start()
                body=string[body_start:]
                slug = splitext(basename(self._path))[0] # use the file name
                post= Post(title=t,slug=slug,body=body,category=c,author=u)
                tags =re.search(r'\[(.*)\]',match.group('tags'))

                for tag in change_tags(tags.group(1)):
                    if tag:
                        post.tags.append(tag)

                db.session.add(post)
                db.session.commit()
        elif self._type == ".html":
            print "add a new html file,%s"%self._path

def init_app(app):
    import time
    file_watch = FileWatch(app)
    observer=Observer()
    observer.schedule(
        file_watch,
        path=file_watch.app.config["CONTENT_PATH"],
        recursive=True
    )
    observer.start()

    # try:
    #     while True:
    #         time.sleep(1)
    # except KeyboardInterrupt:
    #    observer.stop()
    # observer.join()
