#!/usr/bin/env python
from django.core.management import execute_manager
import sys, os
import settings

sys.path.insert(0, os.path.join(settings.PROJECT_ROOT, "apps"))

if __name__ == "__main__":
    execute_manager(settings)
