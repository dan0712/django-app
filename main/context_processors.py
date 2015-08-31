__author__ = 'cristian'

from django.conf import settings # import the settings file


def site_contact(request):
    # return the value you want as a dictionnary. you may add multiple values in there.
    return {'SUPPORT_EMAIL': settings.SUPPORT_EMAIL,
            'SUPPORT_PHONE': settings.SUPPORT_PHONE}