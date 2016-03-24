__author__ = 'cristian'

from django.conf import settings  # import the settings file
from django.utils.safestring import mark_safe


def site_contact(request):
    # return the value you want as a dictionary. you may add multiple values in there.
    csrf_meta = """<meta content="csrfmiddlewaretoken" name="csrf-param">
    <meta content="{0}" name="csrf-token">""".format(request.META["CSRF_COOKIE"])

    return {'SUPPORT_EMAIL': settings.SUPPORT_EMAIL,
            'SUPPORT_PHONE': settings.SUPPORT_PHONE,
            'csrf_meta': mark_safe(csrf_meta)
            }
