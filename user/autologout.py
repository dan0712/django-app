from calendar import timegm

from django.conf import settings
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from django.utils import timezone


class SessionExpireMiddleware:
    def process_request(self, request):
        assert hasattr(request, 'session'), (
            "The Django authentication middleware requires session middleware "
            "to be installed. Edit your MIDDLEWARE_CLASSES setting to insert "
            "'django.contrib.sessions.middleware.SessionMiddleware' before "
            "'django.contrib.auth.middleware.AuthenticationMiddleware'."
        )

        expire_at = request.session.get('__expire_at')
        if expire_at:
            now = timegm(timezone.now().utctimetuple())
            if expire_at < now:
                print('-- Flushed')
                request.session.flush()
            else:
                print('-- Extended')
                request.session['__expire_at'] = now + settings.SESSION_LENGTH


@receiver(user_logged_in)
def set_session_expiration_time(sender, request, user, **kwargs):
    now = timegm(timezone.now().utctimetuple())
    request.session['__expire_at'] = now + settings.SESSION_LENGTH
