from django.core.exceptions import ObjectDoesNotExist
from rest_framework.generics import RetrieveAPIView
from rest_framework import status
from api.v1.views import ApiViewMixin
from main.models import Firm
from support.models import SupportRequest
from .serializers import FirmSerializer
from rest_framework.response import Response
import logging

logger = logging.getLogger('api.v1.firm.views')


class FirmSingleView(ApiViewMixin, RetrieveAPIView):
    serializer_class = FirmSerializer

    def get(self, request, pk):
        user = SupportRequest.target_user(request)
        serializer = None
        if user.is_advisor:
            if user.advisor.firm.pk == int(pk):
                serializer = self.serializer_class(user.advisor.firm)
        elif user.is_authorised_representative:
            if user.authorised_representative.firm.pk == int(pk):
                serializer = self.serializer_class(user.authorised_representative.firm)
        elif user.is_supervisor:
            if user.supervisor.firm.pk == int(pk):
                serializer = self.serializer_class(user.supervisor.firm)
        elif user.is_client:
            # make sure user is a client of the requested firm
            try:
                firm = Firm.objects.get(pk=pk)
            except:
                return Response('Firm not found', status=status.HTTP_404_NOT_FOUND)
            if user.client in firm.get_clients():
                serializer = self.serializer_class(firm)

        if serializer:
            return Response(serializer.data)
        return self.permission_denied(request)
