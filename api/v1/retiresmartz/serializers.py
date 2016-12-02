import logging
from datetime import date

from django.conf import settings
from django.db import transaction
from django.template import RequestContext
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.functional import curry
from django.utils.timezone import now
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from api.v1.goals.serializers import PortfolioSerializer
from api.v1.serializers import ReadOnlyModelSerializer
from client.models import Client, ClientAccount
from main import constants
from main.models import ExternalAsset
from main.risk_profiler import GoalSettingRiskProfile
from retiresmartz.models import RetirementAdvice, RetirementPlan, \
    RetirementPlanEinc


logger = logging.getLogger('api.v1.retiresmartz.serializers')


def get_default_tx_plan():
    return {
        'begin_date': now().today().date(),
        'amount': 0,
        'growth': settings.BETASMARTZ_CPI,
        'schedule': 'RRULE:FREQ=MONTHLY;BYMONTHDAY=1'
    }


def get_default_life_expectancy(client):
    return settings.MALE_LIFE_EXPECTANCY if client.gender == constants.GENDER_MALE else settings.FEMALE_LIFE_EXPECTANCY


def get_default_retirement_date(client):
    return date(client.date_of_birth.year + 67, client.date_of_birth.month, client.date_of_birth.day)


def who_validator(value):
    if value not in ['self', 'partner', 'joint']:
        raise ValidationError("'who' must be (self|partner|joint)")


def make_category_validator(category):
    def category_validator(value):
        if category(value) not in category:
            raise ValidationError("'cat' for %s must be one of %s" % (category, category.choices()))
    return category_validator


def make_json_list_validator(field, serializer):
    def list_item_validator(value):
        if not isinstance(value, list):
            raise ValidationError("%s must be a JSON list of objects" % field)
        for item in value:
            if not isinstance(item, dict) or not serializer(data=item).is_valid(raise_exception=True):
                raise ValidationError("Invalid %s object" % field)
    return list_item_validator


class PartnerDataSerializer(serializers.Serializer):
    name = serializers.CharField()
    dob = serializers.DateField()
    ssn = serializers.CharField(),
    retirement_age = serializers.IntegerField(default=67)
    income = serializers.IntegerField()
    smoker = serializers.BooleanField(default=False)
    daily_exercise = serializers.IntegerField(default=0)
    weight = serializers.IntegerField(default=65)
    height = serializers.IntegerField(default=160)
    btc = serializers.IntegerField(required=False)
    atc = serializers.IntegerField(required=False)
    max_match = serializers.FloatField(required=False)
    calculated_life_expectancy = serializers.IntegerField(required=False)
    selected_life_expectancy = serializers.IntegerField(required=False)
    social_security_statement = serializers.FileField(required=False),
    social_security_statement_data = serializers.JSONField(required=False)


def partner_data_validator(value):
    if not isinstance(value, dict) or not PartnerDataSerializer(data=value).is_valid(raise_exception=True):
        raise ValidationError("Invalid partner_data object")


class ExpensesSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    desc = serializers.CharField()
    cat = serializers.IntegerField(validators=[make_category_validator(RetirementPlan.ExpenseCategory)])
    who = serializers.CharField(validators=[who_validator])
    amt = serializers.IntegerField()


class SavingsSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    desc = serializers.CharField()
    cat = serializers.IntegerField(validators=[make_category_validator(RetirementPlan.SavingCategory)])
    who = serializers.CharField(validators=[who_validator])
    amt = serializers.IntegerField()


class InitialDepositsSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    asset = serializers.IntegerField(required=False)
    goal = serializers.IntegerField(required=False)
    amt = serializers.IntegerField()


class RetirementPlanSerializer(ReadOnlyModelSerializer):
    # We need to force JSON output for the JSON fields....
    expenses = serializers.JSONField()
    savings = serializers.JSONField()
    initial_deposits = serializers.JSONField()
    partner_data = serializers.JSONField()
    portfolio = PortfolioSerializer()
    on_track = serializers.BooleanField()
    statement_of_advice = serializers.PrimaryKeyRelatedField(read_only=True)
    statement_of_advice_url = serializers.SerializerMethodField(required=False)

    class Meta:
        model = RetirementPlan
        # Goal setting is an internal field that doesn't need to be shared externally.
        exclude = ('goal_setting',)

    def get_statement_of_advice_url(self, obj):
        if hasattr(obj, 'statement_of_advice'):
            return '/statements/retirement/{}.pdf'.format(obj.statement_of_advice.id)
        else:
            return None


class RetirementPlanWritableSerializer(serializers.ModelSerializer):
    expenses = serializers.JSONField(required=False,
                                     help_text=RetirementPlan._meta.get_field('expenses').help_text,
                                     validators=[make_json_list_validator('expenses', ExpensesSerializer)])
    savings = serializers.JSONField(required=False,
                                    help_text=RetirementPlan._meta.get_field('savings').help_text,
                                    validators=[make_json_list_validator('savings', SavingsSerializer)])
    initial_deposits = serializers.JSONField(required=False,
                                             help_text=RetirementPlan._meta.get_field('initial_deposits').help_text,
                                             validators=[make_json_list_validator('initial_deposits',
                                                                                  InitialDepositsSerializer)])
    selected_life_expectancy = serializers.IntegerField(required=False)
    retirement_age = serializers.IntegerField(required=False)
    desired_risk = serializers.FloatField(required=False)
    btc = serializers.FloatField(required=False)
    atc = serializers.FloatField(required=False)
    retirement_postal_code = serializers.CharField(max_length=10, required=False)
    partner_data = serializers.JSONField(required=False, validators=[partner_data_validator])

    class Meta:
        model = RetirementPlan
        fields = (
            'name',
            'description',
            'partner_plan',
            'lifestyle',
            'desired_income',
            'income',
            'volunteer_days',
            'paid_days',
            'same_home',
            'same_location',
            'retirement_postal_code',
            'reverse_mortgage',
            'retirement_home_style',
            'retirement_home_price',
            'beta_partner',
            'expenses',
            'savings',
            'initial_deposits',
            'income_growth',
            'expected_return_confidence',
            'retirement_age',
            'btc',
            'atc',
            'max_employer_match_percent',
            'desired_risk',
            'selected_life_expectancy',
            'partner_data',
            'agreed_on',
        )

    def __init__(self, *args, **kwargs):
        super(RetirementPlanWritableSerializer, self).__init__(*args, **kwargs)

        # request-based validation
        request = self.context.get('request')
        if request.method == 'PUT':
            for field in self.fields.values():
                field.required = False

    def validate(self, data):
        """
        Define custom validator so we can confirm if same_home is not true, same_location is specified.
        :param data:
        :return:
        """
        if (self.context.get('request').method == 'POST' and not data.get('same_home', None)
                and data.get('same_location', None) is None):
            raise ValidationError("same_location must be specified if same_home is not True.")

        return data

    @transaction.atomic
    def create(self, validated_data):
        client = validated_data['client']
        if not validated_data.get('retirement_postal_code', ''):
            if validated_data['same_home'] or validated_data['same_location']:
                postal_code = client.residential_address.post_code
                validated_data['retirement_postal_code'] = postal_code
            else:
                raise ValidationError('retirement_postal_code required if not same_home and not same_location')
        # Default the selected life expectancy to the calculated one if not specified.
        if not validated_data.get('selected_life_expectancy', None):
            validated_data['selected_life_expectancy'] = client.life_expectancy

        if not validated_data.get('retirement_age', None):
            validated_data['retirement_age'] = 67

        if not validated_data.get('btc', None):
            # defaults btc
            validated_data['btc'] = validated_data['income'] * min(validated_data.get('max_employer_match_percent', 0), 0.04)

        if not validated_data.get('atc', None):
            # default atc
            validated_data['atc'] = 0

        if validated_data['reverse_mortgage'] and validated_data.get('retirement_home_price', None) is None:
            home = client.external_assets.filter(type=ExternalAsset.Type.FAMILY_HOME.value).first()
            if home:
                validated_data['retirement_home_price'] = home.get_growth_valuation(timezone.now().date())

        # Use the recommended risk for the client if no desired risk specified.
        if not validated_data.get('desired_risk', None):
            bas_scores = client.get_risk_profile_bas_scores()
            validated_data['desired_risk'] = GoalSettingRiskProfile._recommend_risk(bas_scores)

        plan = RetirementPlan.objects.create(**validated_data)
        if plan.agreed_on: plan.generate_soa()

        return plan

    @transaction.atomic
    def update(self, instance, validated_data):
        """
        Override the default update because we have nested relations.
        :param instance:
        :param validated_data:
        :return: The updated RetirementPlan
        """

        if instance.agreed_on:
            raise ValidationError("Unable to make changes to a plan that has been agreed on")

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        reverse_plan = getattr(instance, 'partner_plan_reverse', None)
        if instance.partner_plan is not None and reverse_plan is not None and instance.partner_plan != reverse_plan:
            emsg = "Partner plan relationship must be symmetric. " \
                   "I.e. Your selected partner plan must have you as it's partner"
            raise ValidationError(emsg)

        instance.save()

        return instance


class RetirementPlanEincSerializer(ReadOnlyModelSerializer):
    class Meta:
        model = RetirementPlanEinc


class RetirementPlanEincWritableSerializer(serializers.ModelSerializer):
    class Meta:
        model = RetirementPlanEinc
        fields = (
            'name',
            'plan',
            'begin_date',
            'amount',
            'growth',
            'schedule'
        )

    def __init__(self, *args, **kwargs):
        super(RetirementPlanEincWritableSerializer, self).__init__(*args, **kwargs)
        request = self.context.get('request')
        if request.method == 'PUT':
            for field in self.fields.values():
                field.required = False


class RetirementAdviceReadSerializer(ReadOnlyModelSerializer):
    """
        Read-Only RetirementAdvice serializer, used for 
        get request for retirement-plans advice-feed endpoint
    """

    class Meta:
        model = RetirementAdvice
        fields = (
            'id',
            'plan',
            'dt',
            'trigger',
            'text',
            'read',
            'action',
            'action_url',
            'action_data',
        )


class RetirementAdviceWritableSerializer(serializers.ModelSerializer):
    """
        UPDATE PUT/POST RetirementAdvice serializer, used for 
        put requests for retirement-plans advice-feed endpoint
    """
    class Meta:
        model = RetirementAdvice
        fields = (
            'read',
        )

    def __init__(self, *args, **kwargs):
        super(RetirementAdviceWritableSerializer, self).__init__(*args, **kwargs)
        request = self.context.get('request')
        if request.method == 'PUT':
            for field in self.fields.values():
                field.required = False


class NewAccountFabricBase(serializers.Serializer):
    def save(self, request, client) -> ClientAccount:
        raise NotImplementedError()


def new_account_fabric(data: dict) -> NewAccountFabricBase:
    try:
        account_type = data['account_type']
    except KeyError:
        raise ValidationError({'account_type': 'Field not found.'})

    if account_type == constants.ACCOUNT_TYPE_JOINT:
        serializer_class = JointAccountConfirmation
    elif account_type == constants.ACCOUNT_TYPE_TRUST:
        serializer_class = AddTrustAccount
    else:
        serializer_class = AddRolloverAccount
    return serializer_class(data=data)


class JointAccountConfirmation(NewAccountFabricBase):
    email = serializers.EmailField()
    ssn = serializers.CharField()

    client = None

    def validate(self, attrs):
        try:
            self.client = Client.objects.get(user__email=attrs['email'])
            if self.client.regional_data['ssn'] != attrs['ssn']:
                raise ValueError
        except (Client.DoesNotExist, TypeError, KeyError, ValueError):
            raise ValidationError({'email': 'User cannot be found.'})
        return attrs

    def save(self, request, client):
        cosignee = self.client
        account = ClientAccount.objects.create(
            account_type=constants.ACCOUNT_TYPE_JOINT,
            account_name='JOINT {:%Y-%m-%d %H:%M:%S}'.format(now()),
            primary_owner=client,
            default_portfolio_set=client.advisor.default_portfolio_set,
        )
        account.signatories = [cosignee]
        account.save()
        context = RequestContext(request, {
            'sender': client,
            'cosignee': cosignee,
            'account': account,
            'link': '',
            # 'link': reverse('api:v1:client-retirement-plans-joint-confirm',
            #                 kwargs={'parent_lookup_client': client.id, }),
        })
        render = curry(render_to_string, context=context)
        # cosignee.user.email_user(
        #     render('email/client/joint-confirm/subject.txt').strip(),
        #     message=render('email/client/joint-confirm/message.txt'),
        #     html_message=render('email/client/joint-confirm/message.html'),
        # )
        return account


class AddTrustAccount(NewAccountFabricBase):
    trust_legal_name = serializers.CharField()
    trust_nickname = serializers.CharField()
    trust_state = serializers.CharField()
    establish_date = serializers.DateField()
    ein = serializers.CharField(required=False)
    ssn = serializers.CharField(required=False)
    address = serializers.CharField()
    city = serializers.CharField()
    state = serializers.CharField()
    zip = serializers.CharField()

    def validate(self, attrs):
        if not (attrs['ein'] or attrs['ssn']):
            raise ValidationError({
                'ein': 'Either EIN or SSN must present.',
                'ssn': 'Either EIN or SSN must present.',
            })
        return attrs

    def save(self, request, client):
        data = self.validated_data
        account = ClientAccount.objects.create(
            account_type=constants.ACCOUNT_TYPE_TRUST,
            account_name=data['trust_nickname'],
            primary_owner=client,
            default_portfolio_set=client.advisor.default_portfolio_set,
            confirmed=True,
        )
        # todo save trust info
        return account


class AddRolloverAccount(NewAccountFabricBase):
    provider = serializers.CharField()
    account_type = serializers.ChoiceField(choices=constants.ACCOUNT_TYPES)
    account_number = serializers.CharField()
    amount = serializers.FloatField()
    signature = serializers.CharField()

    def save(self, request, client):
        data = self.validated_data
        account_type = data['account_type']
        account = ClientAccount.objects.create(
            account_type=account_type,
            account_name=dict(constants.ACCOUNT_TYPES)[account_type],
            primary_owner=client,
            default_portfolio_set=client.advisor.default_portfolio_set,
            confirmed=True,
        )
        # TODO save source account rollover data
        return account
