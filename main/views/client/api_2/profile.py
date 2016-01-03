from main.models import Client, User
from rest_framework import serializers, viewsets
from .urls import router

__all__ = ["PersonalInfoViewSet", "UserViewSet"]


# Serializers define the API representation.
class PersonalInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = ('pk', 'net_worth', 'income', 'city', 'state', 'address_line_1', 'address_line_2',
                  'post_code', 'phone', 'employment_status', 'create_date', 'states_codes')
        read_only_fields = ('states_codes', )


# ViewSets define the view behavior.
class PersonalInfoViewSet(viewsets.ModelViewSet):
    queryset = Client.objects

    def get_queryset(self):
        # only show the profile of the current user
        return self.queryset.filter(user=self.request.user)
    serializer_class = PersonalInfoSerializer

router.register(r'personal_info', PersonalInfoViewSet)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('pk', 'first_name', 'middle_name', 'last_name', 'email', 'date_joined')


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects

    def get_queryset(self):
        # only show the objects related to the current user
        return self.queryset.filter(pk=self.request.user.pk)
    serializer_class = UserSerializer

router.register(r'user', UserViewSet)
