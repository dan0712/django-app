import re
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .renderers import ApiRenderer


def get_nested_data(data, namespace):
    """
    Helper to get dict of data['namespace'] properties, dropping namespace.
    Used for "post" endpoints to transform flat objects to nested-like ones.
    """
    re_in = r'^' + namespace + '(.*)'
    re_out = r'\1'
    nested_data = {}

    for prop in data:
        nested_prop = re.sub(re_in, re_out, prop)

        # skip empty or non matched properties
        if nested_prop and nested_prop != prop:
            nested_data[nested_prop] = data[prop]

    return nested_data


class MultipleSerializersModelViewMixin(object):
    """
    Experimental

    Let to assign request/reponse serializers for ModelViews.
    (supposed to be used for POST/PUT requests)

    Example:
    serializer_class = ItemSerializer
    serializer_response_class = ItemResponseSerializer
    """

    def get_serializer(self, *args, **kwargs):
        """
        Let to override default serializer passing it as an extra param.
        """
        serializer_class = kwargs.pop('serializer_class', None)

        if not serializer_class and hasattr(self, 'get_serializer_class'):
            serializer_class = self.get_serializer_class()

        if not serializer_class and hasattr(self, 'serializer_class'):
            serializer_class = self.serializer_class

        if hasattr(self, 'get_serializer_context'):
            kwargs['context'] = self.get_serializer_context()

        return serializer_class(*args, **kwargs)

    def create(self, request, *args, **kwargs):
        """
        Override CreateModelMixin to use "response" serializer
        https://github.com/tomchristie/django-rest-framework/blob/master/
            rest_framework/mixins.py
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # patch to use the object returned from save
        saved = self.perform_create(serializer)
        klass = getattr(self, 'serializer_response_class', None)
        serializer = self.get_serializer(instance=saved,
                                         serializer_class=klass)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED,
                        headers=headers)

    def perform_create(self, serializer):
        # patch to return the object
        return serializer.save()

    def update(self, request, *args, **kwargs):
        """
        Override UpdateModelMixin to use "response" serializer
        https://github.com/tomchristie/django-rest-framework/blob/master/
            rest_framework/mixins.py
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data,
                                         partial=partial)
        serializer.is_valid(raise_exception=True)

        # patch to use the object returned from update
        saved = self.perform_update(serializer)
        klass = getattr(self, 'serializer_response_class', None)
        serializer = self.get_serializer(instance=saved,
                                         serializer_class=klass)

        return Response(serializer.data)

    def perform_update(self, serializer):
        # patch to return the object
        return serializer.save()


class ReadOnlyApiViewMixin(object):
    permission_classes = IsAuthenticated,

    renderer_classes = (
        ApiRenderer,
    )

    def get_nested_data(self, namespace):
        data = self.request.data
        return get_nested_data(data, namespace)


class ApiViewMixin(ReadOnlyApiViewMixin, MultipleSerializersModelViewMixin):
    pass


class BaseApiView(ApiViewMixin, APIView):
    pass
