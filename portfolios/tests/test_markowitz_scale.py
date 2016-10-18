from django.test import TestCase

from portfolios.markowitz_scale import get_risk_curve, _to_lambda, _to_risk_score


class MarkowitzScaleTest(TestCase):

    def test_get_risk_curve_under(self):
        """
        The params we get from get_risk_curve should get us the right lambdas when fed back in.
        """
        a, b, c = get_risk_curve(0, 0.711)

        # We know from above our min lambda should be 0 and max 0.711
        self.assertAlmostEqual(_to_lambda(0, a, b, c), 0, 6)
        self.assertAlmostEqual(_to_lambda(1, a, b, c), 0.71100, 5)

        # test the return trip
        lam = _to_lambda(0.7, a, b, c)
        self.assertAlmostEqual(_to_risk_score(lam, a, b, c), 0.7, 5)

    def test_get_risk_curve_over(self):
        a, b, c = get_risk_curve(0.03, 12.711)

        self.assertAlmostEqual(_to_lambda(0, a, b, c), 0.03, 5)
        # as the avg is over 1.2, we use 1.2 for the midpoint.
        self.assertAlmostEqual(_to_lambda(0.5, a, b, c), 1.2, 5)

        # test the return trip
        lam = _to_lambda(0.2, a, b, c)
        self.assertAlmostEqual(_to_risk_score(lam, a, b, c), 0.2, 5)
