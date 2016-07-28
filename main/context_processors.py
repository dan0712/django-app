from django.conf import settings
from django.utils.safestring import mark_safe


def site_contact(request):
    """
    Return the value you want as a dictionary.
    You may add multiple values in there.
    """
    csrf_meta = """<meta content="csrfmiddlewaretoken" name="csrf-param">
    <meta content="%s" name="csrf-token">""" % request.META["CSRF_COOKIE"]

    return {
        'SUPPORT_EMAIL': settings.SUPPORT_EMAIL,
        'SUPPORT_PHONE': settings.SUPPORT_PHONE,
        'csrf_meta': mark_safe(csrf_meta),
    }
