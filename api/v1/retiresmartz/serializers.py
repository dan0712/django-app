from datetime import date

from django.conf import settings
from django.db import transaction
from django.utils import timezone
from django.utils.timezone import now
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from api.v1.serializers import ReadOnlyModelSerializer
from main.constants import GENDER_MALE
from main.models import ExternalAsset
from main.risk_profiler import GoalSettingRiskProfile
from retiresmartz.models import RetirementPlan, RetirementPlanEinc, RetirementAdvice


def get_default_tx_plan():
    return {
        'begin_date': now().today().date(),
        'amount': 0,
        'growth': settings.BETASMARTZ_CPI,
        'schedule': 'RRULE:FREQ=MONTHLY;BYMONTHDAY=1'
    }


def get_default_life_expectancy(client):
    return settings.MALE_LIFE_EXPECTANCY if client.gender == GENDER_MALE else settings.FEMALE_LIFE_EXPECTANCY


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

    class Meta:
        model = RetirementPlan


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
            'recommended_risk',
            'max_risk',
            'selected_life_expectancy',
            'portfolio',
            'partner_data',
            'agreed_on',
            'on_track',
        )
        read_only_fields = (
            'portfolio',
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
            validated_data['btc'] = validated_data['income'] * 0.04

        if not validated_data.get('atc', None):
            validated_data['atc'] = 0

        if validated_data['reverse_mortgage'] and validated_data.get('retirement_home_price', None) is None:
            home = client.external_assets.filter(type=ExternalAsset.Type.FAMILY_HOME).first()
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
