#!/usr/bin/env python
from gevent import monkey
monkey.patch_all()

from socketio import SocketIOServer
import django.core.handlers.wsgi
import os
import sys

import settings

PORT = 9000

os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
application = django.core.handlers.wsgi.WSGIHandler()

sys.path.insert(0, os.path.join(settings.PROJECT_ROOT, "../"))
sys.path.insert(0, os.path.join(settings.PROJECT_ROOT, "apps"))

if __name__ == '__main__':
    print('Listening on http://127.0.0.1:%s and on port 843 (flash policy server)' % PORT)
    SocketIOServer(('', PORT), application, resource="socket.io").serve_forever()
