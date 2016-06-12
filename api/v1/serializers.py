from collections import OrderedDict

from rest_framework import serializers
from rest_framework.fields import SkipField


class NoUpdateModelSerializer(serializers.ModelSerializer):
    def update(self, instance, validated_data):
        raise NotImplementedError('update is not a valid operation for a NoUpdateModelSerializer')


class NoCreateModelSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        raise NotImplementedError('create is not a valid operation for a NoCreateModelSerializer')


class ReadOnlyModelSerializer(serializers.ModelSerializer):
    def save(self):
        raise NotImplementedError('Save is not a valid operation for a ReadOnlyModelSerializer')

    def update(self, validated_data):
        raise NotImplementedError('update is not a valid operation for a ReadOnlyModelSerializer')

    def create(self):
        raise NotImplementedError('create is not a valid operation for a ReadOnlyModelSerializer')

    def __init__(self, *args, **kwargs):
        super(ReadOnlyModelSerializer, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.read_only = True


class QueryParamSerializer(serializers.Serializer):
    @classmethod
    def parse(cls, query_params):
        serializer = QueryParamSerializer(data=query_params)
        serializer.is_valid(raise_exception=True)
        return serializer.validated_data


class NonNullModelSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        """
        Object instance -> Dict of primitive datatypes.
        """
        ret = OrderedDict()
        fields = [field for field in self.fields.values() if not field.write_only]

        for field in fields:
            try:
                attribute = field.get_attribute(instance)
            except SkipField:
                continue

            if attribute is not None:
                represenation = field.to_representation(attribute)
                if represenation is None:
                    # Do not serialize null objects
                    continue
                ret[field.field_name] = represenation

        return ret
