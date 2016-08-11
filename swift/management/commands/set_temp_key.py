# -*- coding: utf-8 -*-
# author: Glen Baker <iepathos@gmail.com>
from django.core.management import BaseCommand
import logging
import subprocess as sp
logging.basicConfig(level=logging.ERROR)
logging.getLogger("requests").setLevel(logging.CRITICAL)
logging.getLogger("swiftclient").setLevel(logging.CRITICAL)
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Set the temporary url key for softlayer cloud storage."

    def add_arguments(self, parser):
        parser.add_argument('key', nargs=1, type=str)

    def handle(self, *args, **options):
        # swift post -m "Temp-URL-Key:${1}"
        data = "Temp-URL-Key:%s" % options['key'][0]
        out = sp.check_output(['swift', 'post', '-m', data])
        if out == b'':
            logger.info('Success')
        else:
            logger.error('Failed to set Temp URL Key \n%b' % out)
