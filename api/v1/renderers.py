import logging

from rest_framework.renderers import JSONRenderer

from api.v1.user.serializers import UserSerializer
from support.models import SupportRequest
from user.autologout import SessionExpire


# format json response
# https://google-styleguide.googlecode.com/svn/trunk/jsoncstyleguide.xml
class ApiRenderer(JSONRenderer):

    def render(self, data, media_type=None, renderer_context=None):
        """
        NB. be sure that settings.REST_FRAMEWORK contains:
        'EXCEPTION_HANDLER': '...api_exception_handler',
        """
        logger = logging.getLogger(__name__)
        wrapper = {
            'version': '2',
            'data': {},
            'meta': {},
        }

        # move error to the root level
        if hasattr(data, 'get') and data.get('error'):
            wrapper['error'] = data['error']
            del data['error']

        if data is not None:
            wrapper['data'] = data

        try:
            response = renderer_context['response']
            request = renderer_context['request']
            if 200 <= response.status_code < 400:
                meta = {}
                session_expire = SessionExpire(request)
                meta['session_expires_on'] = session_expire.expire_time()

                sr = SupportRequest.get_current(request, as_obj=True)
                if sr:
                    meta['support_request'] = {
                        'ticket': sr.ticket,
                        'user': UserSerializer(instance=sr.user).data,
                    }

                wrapper['meta'] = meta
        except (TypeError, KeyError) as e:
            logger.error("Missing parameteres (%s)", e)

        return super(ApiRenderer, self).render(wrapper, media_type,
                                               renderer_context)
