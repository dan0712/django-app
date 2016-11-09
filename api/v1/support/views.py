import logging
from datetime import date
from dateutil.relativedelta import relativedelta
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import detail_route
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from api.v1.views import BaseApiView
from support.models import SupportRequest
from . import serializers
from .emails import request_advisor_support
from api.v1.permissions import IsClient
logger = logging.getLogger('api.v1.support.views')


class RequestAdvisorSupportView(BaseApiView):
    serializer_class = serializers.RequestAdvisorSupportSerializer
    permission_classes = IsClient,

    def post(self, request):
        user = SupportRequest.target_user(self.request)
        if user.is_client:
            serializer = self.serializer_class(data=request.data)
            serializer.is_valid(raise_exception=True)
            request_advisor_support(user,
                                    serializer.validated_data['url'],
                                    serializer.validated_data.get('text', None))
            return Response('ok', status=status.HTTP_200_OK)
        else:
            return Response('User is not a client', status=status.HTTP_401_UNAUTHORIZED)
