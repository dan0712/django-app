import datetime

from django.utils import timezone
from pinax.eventlog.models import Log

from main.event import Event
from main.models import ClientAccount, ACCOUNT_TYPE_PERSONAL, Client, Advisor, User, Firm, PortfolioSet, \
    RiskProfileGroup, GoalSetting, GoalMetricGroup, Goal, GoalType, RiskProfileQuestion, RiskProfileAnswer, Transaction, \
    HistoricalBalance


class Fixture1:
    @classmethod
    def portfolioset1(cls):
        params = {
            'name': 'portfolioset1',
            'risk_free_rate': 0.02,
        }
        return PortfolioSet.objects.get_or_create(id=1, defaults=params)[0]

    @classmethod
    def firm1(cls):
        params = {
            'name': 'example_inc',
            'token': 'example_inc',
            'default_portfolio_set': Fixture1.portfolioset1(),
        }
        return Firm.objects.get_or_create(slug='example_inc', defaults=params)[0]

    @classmethod
    def advisor1_user(cls):
        params = {
            'first_name': "test",
            'last_name': "advisor",
        }
        return User.objects.get_or_create(email="advisor@example.com", defaults=params)[0]

    @classmethod
    def advisor1(cls):
        params = {
            'firm': Fixture1.firm1(),
            'betasmartz_agreement': True,
            'default_portfolio_set': Fixture1.portfolioset1(),
        }
        return Advisor.objects.get_or_create(user=Fixture1.advisor1_user(), defaults=params)[0]

    @classmethod
    def client1_user(cls):
        params = {
            'first_name': "test",
            'last_name': "client",
        }
        return User.objects.get_or_create(email="client@example.com", defaults=params)[0]

    @classmethod
    def client1(cls):
        params = {
            'advisor': Fixture1.advisor1(),
            'user': Fixture1.client1_user(),
            'date_of_birth': datetime.date(1970, 1, 1)
        }
        return Client.objects.get_or_create(id=1, defaults=params)[0]

    @classmethod
    def risk_profile_group1(cls):
        return RiskProfileGroup.objects.get_or_create(name='risk_profile_group1')[0]

    @classmethod
    def risk_profile_question1(cls):
        return RiskProfileQuestion.objects.get_or_create(group=Fixture1.risk_profile_group1(),
                                                         order=0,
                                                         text='How much do you like risk?')[0]

    @classmethod
    def risk_profile_question2(cls):
        return RiskProfileQuestion.objects.get_or_create(group=Fixture1.risk_profile_group1(),
                                                         order=1,
                                                         text='How sophisticated are you?')[0]

    @classmethod
    def risk_profile_answer1a(cls):
        return RiskProfileAnswer.objects.get_or_create(question=Fixture1.risk_profile_question1(),
                                                       order=0,
                                                       text='A lot',
                                                       score=9)[0]

    @classmethod
    def risk_profile_answer1b(cls):
        return RiskProfileAnswer.objects.get_or_create(question=Fixture1.risk_profile_question1(),
                                                       order=1,
                                                       text='A little',
                                                       score=2)[0]

    @classmethod
    def risk_profile_answer2a(cls):
        return RiskProfileAnswer.objects.get_or_create(question=Fixture1.risk_profile_question2(),
                                                       order=0,
                                                       text='Very',
                                                       score=9)[0]

    @classmethod
    def risk_profile_answer2b(cls):
        return RiskProfileAnswer.objects.get_or_create(question=Fixture1.risk_profile_question2(),
                                                       order=1,
                                                       text="I'm basically a peanut",
                                                       score=1)[0]

    @classmethod
    def populate_risk_profile_questions(cls):
        Fixture1.risk_profile_question1()
        Fixture1.risk_profile_answer1a()
        Fixture1.risk_profile_answer1b()
        Fixture1.risk_profile_question2()
        Fixture1.risk_profile_answer2a()
        Fixture1.risk_profile_answer2b()

    @classmethod
    def populate_risk_profile_responses(cls):
        Fixture1.personal_account1().risk_profile_responses.add(Fixture1.risk_profile_answer1a())
        Fixture1.personal_account1().risk_profile_responses.add(Fixture1.risk_profile_answer2a())

    @classmethod
    def personal_account1(cls):
        params = {
            'account_type': ACCOUNT_TYPE_PERSONAL,
            'primary_owner': Fixture1.client1(),
            'default_portfolio_set': Fixture1.portfolioset1(),
            'risk_profile_group': Fixture1.risk_profile_group1(),
        }
        return ClientAccount.objects.get_or_create(id=1, defaults=params)[0]

    @classmethod
    def metric_group1(cls):
        return GoalMetricGroup.objects.get_or_create(type=GoalMetricGroup.TYPE_PRESET,
                                                     name='metricgroup1')[0]

    @classmethod
    def settings1(cls):
        return GoalSetting.objects.get_or_create(target=100000,
                                                 completion=datetime.date(2000, 1, 1),
                                                 hedge_fx=False,
                                                 metric_group=Fixture1.metric_group1(),
                                                 rebalance=False)[0]

    @classmethod
    def goal_type1(cls):
        return GoalType.objects.get_or_create(name='goaltype1',
                                              default_term=5,
                                              risk_sensitivity=7.0)[0]

    @classmethod
    def goal1(cls):
        return Goal.objects.get_or_create(account=Fixture1.personal_account1(),
                                          name='goal1',
                                          type=Fixture1.goal_type1(),
                                          portfolio_set=Fixture1.portfolioset1(),
                                          selected_settings=Fixture1.settings1())[0]

    @classmethod
    def settings_event1(cls):
        return Log.objects.get_or_create(user=Fixture1.client1_user(),
                                         timestamp=timezone.make_aware(datetime.datetime(2000, 1, 1)),
                                         action=Event.APPROVE_SELECTED_SETTINGS.name,
                                         extra={'reason': 'Just because'},
                                         defaults={'obj': Fixture1.goal1()})[0]

    @classmethod
    def transaction_event1(cls):
        # This will populate the associated Transaction as well.
        return Log.objects.get_or_create(user=Fixture1.client1_user(),
                                         timestamp=timezone.make_aware(datetime.datetime(2001, 1, 1)),
                                         action=Event.GOAL_DEPOSIT_EXECUTED.name,
                                         extra={'reason': 'Goal Deposit',
                                                'txid': Fixture1.transaction1().id},
                                         defaults={'obj': Fixture1.goal1()})[0]

    @classmethod
    def transaction1(cls):
        return Transaction.objects.get_or_create(reason=Transaction.REASON_DEPOSIT,
                                                 to_goal=Fixture1.goal1(),
                                                 amount=3000,
                                                 status=Transaction.STATUS_EXECUTED,
                                                 created=timezone.make_aware(datetime.datetime(2000, 1, 1)),
                                                 executed=timezone.make_aware(datetime.datetime(2001, 1, 1)))[0]

    @classmethod
    def populate_balance1(cls):
        HistoricalBalance.objects.get_or_create(goal=Fixture1.goal1(),
                                                date=datetime.date(2000, 12, 31),
                                                balance=0)
        HistoricalBalance.objects.get_or_create(goal=Fixture1.goal1(),
                                                date=datetime.date(2001, 1, 1),
                                                balance=3000)
