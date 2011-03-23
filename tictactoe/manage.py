#!/usr/bin/env python
from django.core.management import execute_manager
import os, sys

import imp
try:
    imp.find_module('settings') # Assumed to be in the same directory.
except ImportError:
    import sys
    sys.stderr.write("Error: Can't find the file 'settings.py' in the directory containing %r. It appears you've customized things.\nYou'll have to run django-admin.py, passing it your settings module.\n" % __file__)
    sys.exit(1)

import settings

sys.path.insert(0, os.path.join(settings.PROJECT_ROOT, "apps"))

if __name__ == "__main__":
    execute_manager(settings)
