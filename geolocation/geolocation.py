#!/usr/bin/env python
# -*- coding:utf-8 -*-
import pygeoip
from django.conf import settings
import os
import logging

logger = logging.getLogger('geolocation.geolocation')
geolite_db = os.path.join(settings.BASE_DIR, 'geolocation', 'GeoLiteCity.dat')
rawdata = pygeoip.GeoIP(geolite_db)


def check_ip_city(request, city=None):
	"""
	returns True if the given request is from an IP address
	that falls within the given location.
	"""
	remote_address = request.META.get('HTTP_X_FORWARDED_FOR')or request.META.get('REMOTE_ADDR')
	logger.info('Checking geolocation for %s' % remote_address)
	data = rawdata.record_by_name(remote_address)

	x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
	if x_forwarded_for:
		data = rawdata.record_by_name(x_forwarded_for)
	if data:
		if data['city'] == city:
			return True
	return False
