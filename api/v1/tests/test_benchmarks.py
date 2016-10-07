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
        self.assertDictEqual(content['error'], {
            'code': 403,
            'reason': 'NotAuthenticated',
            'message': 'Authentication credentials were not provided.'
        })

    def test_logged_in_access(self):
        self.client.force_authenticate(user=Fixture1.client1().user)
        r = self.request()
        content = ujson.loads(r.content)
        self.assertEqual(content['data'], [])


class SingleBenchmarkTest(BaseApiTest):
    def setUp(self):
        self.market_index = Fixture1.market_index1()
        Fixture1.market_index1_daily_prices()

    def request_urls(self):
        return reverse('api:v1:benchmarks:single', args=[self.market_index.id])

    def test_all_dates(self):
        self.client.force_authenticate(user=Fixture1.client1().user)
        r = self.request(status_code=200)
        content = ujson.loads(r.content)['data']
        self.assertEqual(content, [
            [16893, 0.1],
            [16894, -0.045454545454545005],
            [16895, -0.019047619047619],
            [16896, 0.03883495145631],
        ])

    def test_subset_dates(self):
        self.client.force_authenticate(user=Fixture1.client1().user)
        r = self.request(data={
            'sd': '2016-04-02',
            'ed': '2016-04-04',
        }, status_code=200)
        content = ujson.loads(r.content)['data']
        self.assertEqual(content, [
            [16894, -0.045454545454545005],
            [16895, -0.019047619047619],
        ])

    def test_bottom_bound_dates(self):
        self.client.force_authenticate(user=Fixture1.client1().user)
        r = self.request(data={
            'sd': '2016-04-02',
        }, status_code=200)
        content = ujson.loads(r.content)['data']
        self.assertEqual(content, [
            [16894, -0.045454545454545005],
            [16895, -0.019047619047619],
            [16896, 0.03883495145631],
        ])

    def test_top_bound_dates(self):
        self.client.force_authenticate(user=Fixture1.client1().user)
        r = self.request(data={
            'ed': '2016-04-04',
        }, status_code=200)
        content = ujson.loads(r.content)['data']
        self.assertEqual(content, [
            [16893, 0.1],
            [16894, -0.045454545454545005],
            [16895, -0.019047619047619],
        ])

