from datetime import datetime

from flask import flash, jsonify, redirect, render_template, request, url_for

from . import todo
from .. import db
from ..models import Todo


@todo.route('/')
def index():
    return render_template('Todo/index.html')

@todo.route('/add',methods=['POST',])
def add():
    data = request.data
    content = data("content")
    # import ipdb; ipdb.set_trace()
    todo = Todo(content=content,time=datetime.now())
    db.session.add(todo)
    db.session.commit()
    return jsonify(status=content)

@todo.route('/delete/<string:todo_id>')
def delete(todo_id):
    todo= Todo.query.filter_by(id=2).first()
    db.session.delete(todo)
    db.session.commit()
    return jsonify(status='success')

@todo.route('/update',methods=['POST',])
def update():
    data =request.data
    todo_id=data('id')
    content=data('content')
    todo= Todo.query.filter_by(id=todo_id).first()
    todo.content=content
    db.session.add(todo)
    db.session.commit()
    return jsonify(status='success')


@todo.route('/list')
def list():
    todos= Todo.query.order_by('-time').all()
    return jsonify(status="success",todos=[t.to_json() for t in todos])
