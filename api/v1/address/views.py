import logging
from rest_framework import status
from rest_framework import views
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from address.models import Region
from . import serializers
from ..views import ApiViewMixin

logger = logging.getLogger('api.v1.address.views')


class RegionView(ApiViewMixin, views.APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = serializers.RegionSerializer

    def get(self, request, pk):
        try:
            region = Region.objects.get(pk=pk)
        except:
            logger.error('Region not found with pk %s' % pk)
            return Response('Region not found', status=status.HTTP_404_NOT_FOUND)
        serializer = serializers.RegionSerializer(region, context={'request': request})
        return Response(serializer.data)
