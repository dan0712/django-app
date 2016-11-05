from geolocation.geolocation import rawdata
import unittest


class TestGeolocation(unittest.TestCase):

    def test_recognize_some_ip_cities(self):
        data = rawdata.record_by_name('204.93.210.40')
        self.assertEqual(data['city'], 'Chicago')
        data = rawdata.record_by_name('72.229.28.185')
        self.assertEqual(data['city'], 'New York')
