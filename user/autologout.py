from calendar import timegm
from datetime import datetime

from django.conf import settings
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from django.utils import timezone

__all__ = ['SessionExpire']


class SessionExpire:
    _key_name = '__expire_at'

    def __init__(self, request):
        self.request = request

    def expire_time(self):
        try:
            timestamp = self.request.session[self._key_name]
            return datetime.fromtimestamp(timestamp, timezone.UTC())
        except KeyError:
            pass

    def keep_alive(self):
        now = timegm(timezone.now().utctimetuple())
        self.request.session[self._key_name] = now + settings.SESSION_LENGTH

    def check(self):
        expire_at = self.request.session.get(self._key_name)
        if expire_at:
            now = timegm(timezone.now().utctimetuple())
            if expire_at < now:
                self.request.session.flush()
            else:
                self.keep_alive()


class SessionExpireMiddleware:
    def process_request(self, request):
        assert hasattr(request, 'session'), (
            "The Django authentication middleware requires session middleware "
            "to be installed. Edit your MIDDLEWARE_CLASSES setting to insert "
            "'django.contrib.sessions.middleware.SessionMiddleware' before "
            "'django.contrib.auth.middleware.AuthenticationMiddleware'."
        )
        SessionExpire(request).check()


@receiver(user_logged_in)
def set_session_expiration_time(sender, request, **kwargs):
    SessionExpire(request).keep_alive()
