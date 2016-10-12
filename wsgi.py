#!usr/bin/env python
# -*- coding: utf-8 -*-

from gevent import monkey
monkey.patch_all()

from manage import app as application
from gevent.wsgi import WSGIServer

if __name__ == '__main__':
    http_server = WSGIServer(('', 5000), application)
    http_server.serve_forever()
