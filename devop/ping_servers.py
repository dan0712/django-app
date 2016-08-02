#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This is a basic monitoring script to check the status
of betasmartz web servers.

TODO: Integrate with slack or something we're already using
to send alerts when one of the environments stops responding.
"""
from urllib.request import urlopen
import multiprocessing
import time

__author__ = 'Glen Baker <iepathos@gmail.com>'


production_machine_environments = [
    'www',
    'production',
    'demo',
]

dev_machine_environments = [
    'dev',
    'beta',
    'betastaging',
    'staging',
    'aus',
]


def ping_environment(env):
    print('Checking https://%s.betasmartz.com' % env)
    code = urlopen('https://%s.betasmartz.com' % env).getcode()
    if code == 200:
        print('SUCCESS %s environment responding with code 200' % env)
    else:
        print('ERROR %s responded with code %s' % (env, code))


def ping_all_environments():
    # check production environments first
    pool = multiprocessing.Pool(5)
    production_machine_environments.extend(dev_machine_environments)
    pool.map(ping_environment, production_machine_environments)

try:
    while True:
        ping_all_environments()
        print('Waiting for 5 minutes before checking environments again.')
        # wait 5 minutes and ping again
        time.sleep(300)
except KeyboardInterrupt:
    pass
