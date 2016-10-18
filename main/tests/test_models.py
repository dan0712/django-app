from django.test import TestCase
from api.v1.tests.factories import AdvisorFactory
from main.tests.fixture import Fixture1
import json


class BaseTest(TestCase):
    def o(self, obj):
        return obj.__class__.objects.get(pk=obj.pk)


class RegionalDataTest(BaseTest):
    def test_default_value(self):
        advisor = Fixture1.advisor1()
        self.assertEqual(advisor.regional_data, {})

    def test_assign_invalid_field_name(self):
        advisor = Fixture1.advisor1()
        advisor.regional_data = {
            'us_citizen': True,
        }
        with self.assertRaises(ValueError) as e:
            advisor.clean()
        self.assertEqual(str(e.exception),
                         "{'regional_data': 'Got 1 unknown fields "
                         "(us_citizen).'}")

    def test_assign_invalid_field_value(self):
        advisor = Fixture1.advisor1()
        advisor.regional_data = {
            'provide_tfn': 'yes',
        }
        with self.assertRaises(ValueError) as e:
            advisor.clean()
        self.assertEqual(str(e.exception),
                         "{'regional_data': 'Field provide_tfn has bool type, "
                         "got str.'}")

    def test_saving(self):
        advisor = Fixture1.advisor1()
        advisor.regional_data = {
            'tax_file_number': '1234',
        }
        advisor.clean()
        advisor.save()

        advisor = self.o(advisor)
        self.assertDictEqual(advisor.regional_data, {
            'tax_file_number': '1234',
        })

        advisor.regional_data = ''
        with self.assertRaises(ValueError) as e:
            advisor.clean()
        self.assertEqual(str(e.exception), "{'regional_data': "
                                           "\"Must be 'dict' type.\"}")

        advisor.regional_data = {}
        advisor.clean()
        advisor.save()

        advisor = self.o(advisor)
        self.assertEqual(advisor.regional_data, {})


class AdvisorTest(BaseTest):
    def test_average_client_balance(self):
        advisor = Fixture1.advisor1()
        self.assertEqual(advisor.average_client_balance, 0)

    def test_average_group_balance(self):
        advisor = Fixture1.advisor1()
        self.assertEqual(advisor.average_group_balance, 0)

    def test_tax_transcript(self):
        advisor = AdvisorFactory.create()
        advisor.country = 'US'
        advisor.save()
        test_transcript_data = {'some': 'data'}
        advisor.regional_data = {
            'politically_exposed': True,
            'ssn': '555-55-5555',
            'tax_transcript': 'https://some.url/on/softlayer/cloud/storage',
            'tax_transcript_data': json.dumps(test_transcript_data),
        }
        advisor.clean()
        self.assertEqual(advisor.regional_data.get('tax_transcript'), 'https://some.url/on/softlayer/cloud/storage')
        self.assertEqual(json.loads(advisor.regional_data.get('tax_transcript_data')), test_transcript_data)

    def test_security_statement(self):
        advisor = AdvisorFactory.create()
        advisor.country = 'US'
        advisor.save()
        test_security_statement_data = {'some': 'data'}
        advisor.regional_data = {
            'politically_exposed': True,
            'ssn': '555-55-5555',
            'social_security_statement': 'https://some.url/on/softlayer/cloud/storage',
            'social_security_statement_data': json.dumps(test_security_statement_data),
        }
        advisor.clean()
        self.assertEqual(advisor.regional_data.get('social_security_statement'), 'https://some.url/on/softlayer/cloud/storage')
        self.assertEqual(json.loads(advisor.regional_data.get('social_security_statement_data')), test_security_statement_data)
