from calendar import timegm

from django.conf import settings
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from django.utils import timezone

__all__ = ['keep_alive', 'SessionExpireMiddleware']

key_name = '__expire_at'


def keep_alive(request):
    now = timegm(timezone.now().utctimetuple())
    request.session[key_name] = now + settings.SESSION_LENGTH


class SessionExpireMiddleware:
    def process_request(self, request):
        assert hasattr(request, 'session'), (
            "The Django authentication middleware requires session middleware "
            "to be installed. Edit your MIDDLEWARE_CLASSES setting to insert "
            "'django.contrib.sessions.middleware.SessionMiddleware' before "
            "'django.contrib.auth.middleware.AuthenticationMiddleware'."
        )

        expire_at = request.session.get(key_name)
        if expire_at:
            now = timegm(timezone.now().utctimetuple())
            if expire_at < now:
                request.session.flush()
            else:
                keep_alive(request)


@receiver(user_logged_in)
def set_session_expiration_time(sender, request, **kwargs):
    keep_alive(request)
