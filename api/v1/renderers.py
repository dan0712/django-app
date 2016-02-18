import json

from rest_framework.renderers import JSONRenderer


# format json response
# https://google-styleguide.googlecode.com/svn/trunk/jsoncstyleguide.xml
class ApiRenderer(JSONRenderer):

    def render(self, data, media_type=None, renderer_context=None):
        """
        NB. be sure that settings.REST_FRAMEWORK contains:
        'EXCEPTION_HANDLER': '...api_exception_handler',
        """

        wrapper = {
            'apiVersion': '2',
        }

        # move error to the root level
        if hasattr(data, 'get') and data.get('error'):
            wrapper['error'] = data['error']
            del data['error']

            # move status to the root level
            if data.get('status'):
                wrapper['status'] = data['status']
                del data['status']
            else:
                wrapper['status'] = renderer_context['response'].status_code

        if data:
            wrapper['data'] = data

        return super(ApiRenderer, self).render(wrapper, media_type, renderer_context)
