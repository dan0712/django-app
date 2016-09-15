from main.constants import ACCOUNT_TYPE_JOINT, ACCOUNT_TYPE_PERSONAL, ACCOUNT_TYPE_SMSF

# The risk score if we don't have enough info to say anything.
NEUTRAL_RISK = 0.5

def scale(val, src, dst):
    """
    Scale the given value from the scale of src to the scale of dst.
    """
    return ((val - src[0]) / (src[1]-src[0])) * (dst[1]-dst[0]) + dst[0]

class GoalSettingRiskProfile(object):
    def __init__(self, setting):
        self.setting = setting
        self.account = setting.goal.account
        self.client = self.account.primary_owner

    def get_portfolio_worth(self):
        """
        :return: Portfolio worth as a
        """
        # If the account is a Joint or Personal, use age of youngest owner, otherwise, use None
        if self.account.account_type in (ACCOUNT_TYPE_PERSONAL, ACCOUNT_TYPE_SMSF, ACCOUNT_TYPE_JOINT):
            primary_owner = self.account.primary_owner
            worth = primary_owner.net_worth
            if self.account.account_type == ACCOUNT_TYPE_JOINT:
                joint_holder = self.account.joint_holder.client
                worth += joint_holder.net_worth
        else:
            # TODO: For trusts, use the trust assets as worth
            worth = None
        return worth

    def get_worth_score(self):
        """
        Get the portfolio's ability for a given risk based on net worth
        :return: A risk ability score as a float between 0 and 1
        """
        worth = self.get_portfolio_worth()
        if not worth: return None

        cost = self.setting.goal.total_balance
        relative_cost = cost / worth
        if relative_cost >= 0.5: return 0.1
        if relative_cost <= 0.1: return 1.0
        return scale(relative_cost, (0.5, 0.1), (0.1, 1.0))

    def client_bas_scores(self):
        return self.client.get_risk_profile_bas_scores()

    def goal_bas_scores(self):
        """
        Get BAS scores for a goal, taking into client portfolio's ability
        """
        scores = self.client_bas_scores()
        if not scores: return None
        else: B, A, S = scores
        worth_score = self.get_worth_score()
        if worth_score:
            A = min(worth_score, A)
        return B, A, S

    def recommend_risk(self):
        return self._recommend_risk(self.goal_bas_scores())

    def max_risk(self):
        return self._max_risk(self.goal_bas_scores())

    def risk_data(self):
        scores = self.goal_bas_scores()
        return {
            'recommended': self._recommend_risk(scores),
            'max_risk': self._max_risk(scores),
        }

    @classmethod
    def _recommend_risk(cls, scores):
        """
        Recommend a risk score for the given goal setting
        :param setting: The goal setting to build the recommedation for
        :return: A Float [0-1]
        """
        if not scores: return NEUTRAL_RISK
        else: B, A, S = scores
        return min(B, A, S)

    @classmethod
    def _max_risk(cls, scores):
        """
        Get the max risk [0-1] for a goal, based on
        :return: A risk ability score as a float between 0 and 1
        """
        if not scores: return NEUTRAL_RISK
        else: B, A, S = scores
        return min(A, S)


def recommend_risk(setting):
    return GoalSettingRiskProfile(setting).recommend_risk()

def max_risk(setting):
    return GoalSettingRiskProfile(setting).max_risk()

def recommend_ttl_risks(setting):
    raise NotImplementedError('recommend_ttl_risks has been deprecated, use recommend_risk instead')

def get_risk_willingness(account):
    raise NotImplementedError('get_risk_willingness has been deprecated, use recommend_risk instead')

def risk_data(setting):
    return GoalSettingRiskProfile(setting).risk_data()
