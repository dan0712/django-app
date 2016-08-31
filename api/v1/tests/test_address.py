from rest_framework import status
from rest_framework.test import APITestCase

from django.core.urlresolvers import reverse
from .factories import UserFactory, GroupFactory, ClientFactory, RegionFactory, AddressFactory
from common.constants import GROUP_SUPPORT_STAFF


class AddressTests(APITestCase):
    def setUp(self):
        self.support_group = GroupFactory(name=GROUP_SUPPORT_STAFF)
        self.region = RegionFactory.create()
        self.address = AddressFactory(region=self.region)
        self.user = UserFactory.create()

    def tearDown(self):
        self.client.logout()

    def test_get_region(self):
        url = reverse('api:v1:region-detail', args=[self.region.pk])

        # 403 on unauthenticated requests
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN,
                         msg='403 for unauthenticated request to get region')

        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK,
                         msg='200 returned by authenticated request to get region')

        # make sure expect data is there
        self.assertTrue(response.data['id'] == self.region.pk)
        self.assertTrue(response.data['name'] == self.region.name)
        self.assertTrue(response.data['code'] == self.region.code)
        self.assertTrue(response.data['country'] == self.region.country)

    def test_get_address(self):
        url = reverse('api:v1:address-detail', args=[self.address.pk])

        # 403 on unauthenticated requests
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN,
                         msg='403 for unauthenticated request to get address')

        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK,
                         msg='200 returned by authenticated request to get address')

        self.assertTrue(response.data['id'] == self.address.pk)
        self.assertTrue(response.data['address'] == self.address.address)
        self.assertTrue(response.data['post_code'] == self.address.post_code)
        self.assertTrue(response.data['region']['id'] == self.address.region.pk)
