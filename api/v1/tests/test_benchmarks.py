import ujson

from django.core.urlresolvers import reverse

from api.v1.tests import BaseApiTest
from main.tests.fixture import Fixture1


class BenchmarkListTest(BaseApiTest):
    def request_urls(self):
        return reverse('api:v1:benchmarks:list')

    def tearDown(self):
        self.client.logout()

    def test_anonymous_access_forbidden(self):
        r = self.request()
        content = ujson.loads(r.content)
        self.assertDictEqual(content, {
            'error': {
                'code': 403,
                'message': 'Authentication credentials were not provided.',
                'reason': 'NotAuthenticated',
            }
        })

    def test_logged_in_access(self):
        self.client.force_authenticate(user=Fixture1.client1().user)
        r = self.request()
        content = ujson.loads(r.content)
        self.assertDictEqual(content, {
            'count': 0,
            'next': None,
            'previous': None,
            'results': []
        })
