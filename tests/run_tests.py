#!/usr/bin/env python
import os
import sys

import django
from django.conf import settings
from django.test.utils import get_runner
#from django.test.utils import setup_test_environment

if __name__ == "__main__":
    os.environ['DJANGO_SETTINGS_MODULE'] = 'tests.test_settings'
    django.setup()
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
#    setup_test_environment()
    failures = test_runner.run_tests(["tests"])
    sys.exit(bool(failures))