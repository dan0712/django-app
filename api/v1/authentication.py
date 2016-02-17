from rest_framework import authentication


class ExtraTokenAuthentication(authentication.TokenAuthentication):
    def authenticate(self, request):
        """
        Let to pass token as query param (?token=QWERTY...)
        """
        token = request.GET.get('token', None)
        return self.authenticate_credentials(token) if token else \
            super(ExtraTokenAuthentication, self).authenticate(request)
