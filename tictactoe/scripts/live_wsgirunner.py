#!/usr/bin/env python
from gevent import monkey; monkey.patch_all()
from gevent.wsgi import WSGIServer

import sys
import os
import traceback

from django.core.handlers.wsgi import WSGIHandler
from django.core.management import call_command
from django.core.signals import got_request_exception

sys.path.append('..')
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'


def exception_tracer(sender, **kwargs):
    traceback.print_exc()

got_request_exception.connect(exception_tracer)

call_command('syncdb')
print 'Serving on port 8080'
WSGIServer(('', 8088), WSGIHandler()).serve_forever()
