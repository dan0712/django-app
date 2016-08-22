from rest_framework.test import APITestCase

from main.tests.fixtures import Fixture1


class UserTests(APITestCase):
    def test_login(self):
        url = '/api/v1/login'
        usr = Fixture1.client1_user()
        usr.set_password('temppass')
        usr.save()
        data = {
            'username': usr.email,
            'password': 'temppass',
        }
        response = self.client.post(url, data)
        self.assertIn('sessionid', response.cookies)

