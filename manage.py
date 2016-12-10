#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager, Server, Shell
from flask_whooshalchemyplus import whoosh_index

import app.Watch as FileWatch
from app import create_app, db
from app.models import Category, Permission, Post, Role, Todo, User

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)
migrate = Migrate(app, db)

FileWatch.init_app(app)
whoosh_index(app,Post)

@app.template_filter()
def format_time(s):
    if "|" in s:
        l = str(s).split("|")
        l[0] = l[0] + "年"
        l[1] = l[1] + "月"
        return ''.join(l)
    return s

def make_shell_context():
    return dict(app=app, db=db, User=User, Role=Role, Permission=Permission,Todo=Todo,Category=Category,Post=Post)

manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)
manager.add_command('runserver',Server(host='0.0.0.0',port=9000,use_debugger=True,use_reloader=True))


@manager.command
def test():
    """Run the unit tests."""
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)

@manager.command
def init_db():
    Role.insert_roles()
    c = Category(slug="python",name="python")
    db.session.add(c)
    db.session.commit()

if __name__ == '__main__':
    manager.run()
