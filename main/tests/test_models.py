from django.test import TestCase

from main.tests.fixture import Fixture1


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
