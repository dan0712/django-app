from django.test import TestCase

from main.tests.fixture import Fixture1


class PersonalDataFeatures(TestCase):
    def o(self, obj):
        return obj.__class__.objects.get(pk=obj.pk)

    def test_new_model_has_no_features_set(self):
        advisor = Fixture1.advisor1()
        self.assertEqual(advisor.features, 0)

    def test_assign_invalid_feature(self):
        advisor = Fixture1.advisor1()
        with self.assertRaises(ValueError) as e:
            advisor.features += advisor.US_CITIZEN
        self.assertEqual(str(e.exception),
                         'Unknown %s feature.' % advisor.US_CITIZEN)

    def test_saving(self):
        advisor = Fixture1.advisor1()
        advisor.FEATURES['AU'].append(advisor.US_CITIZEN)
        advisor.features += advisor.US_CITIZEN
        self.assertTrue(advisor.features.has(advisor.US_CITIZEN))
        advisor.save()

        advisor = self.o(advisor)
        self.assertTrue(advisor.features.has(advisor.US_CITIZEN))

        with self.assertRaises(ValueError) as e:
            advisor.features -= advisor.ASSOCIATED_TO_BROKER_DEALER
        self.assertEqual(str(e.exception), 'Unknown %s feature.' %
                         advisor.ASSOCIATED_TO_BROKER_DEALER)

        advisor.features -= advisor.US_CITIZEN
        self.assertFalse(advisor.features.has(advisor.US_CITIZEN))
        advisor.save()

        advisor = self.o(advisor)
        self.assertEqual(advisor.features, 0)
