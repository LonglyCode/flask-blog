#!usr/bin/env python
# -*- coding: utf-8 -*-

from gevent import monkey
from gevent.wsgi import WSGIServer
from manage import app as application

monkey.patch_all()


if __name__ == '__main__':
    http_server = WSGIServer(('', 5000), application)
    http_server.serve_forever()
