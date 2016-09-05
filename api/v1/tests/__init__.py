from rest_framework.test import APITestCase


class BaseApiTest(APITestCase):
    def request(self, method='get', url_name=None, data=None,
                status_code=None):
        """
        :type method: str
        :type url_name: str
        :type data: dict
        :rtype: rest_framework.response.Response
        """
        fn = getattr(self.client, method)
        urls = self.request_urls()
        url = urls if url_name is None else urls[url_name]
        r = fn(url, data, format='json')
        if status_code is not None:
            self.assertEqual(r.status_code, status_code, r.content)
        return r
