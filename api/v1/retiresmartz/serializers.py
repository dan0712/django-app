import json
from datetime import date

from django.conf import settings
from django.db import transaction
from django.utils.timezone import now
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from api.v1.serializers import ReadOnlyModelSerializer
from main.constants import GENDER_MALE
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
        if not value in category:
            raise ValidationError("'cat' for %s must be one of %s" % (category, category.choices()))


def make_json_list_validator(field, serializer):
    def list_item_validator(value):
        try: value = json.loads(value)
        except ValueError: raise ValidationError("Invalid json for %s" % field)
        if not isinstance(value, list):
            raise ValidationError("%s must be a JSON list of objects" % field)
        for item in value:
            if not isinstance(item, dict) or not serializer(data=item).is_valid(raise_exception=True):
                raise ValidationError("Invalid %s object"%field)
    return list_item_validator


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
    class Meta:
        model = RetirementPlan


class RetirementPlanWritableSerializer(serializers.ModelSerializer):
    expenses = serializers.JSONField(required=False,
        help_text = RetirementPlan._meta.get_field('expenses').help_text,
        validators=[make_json_list_validator('expenses', ExpensesSerializer)])
    savings = serializers.JSONField(required=False,
        help_text = RetirementPlan._meta.get_field('savings').help_text,
        validators=[make_json_list_validator('savings', SavingsSerializer)])
    initial_deposits = serializers.JSONField(required=False,
        help_text = RetirementPlan._meta.get_field('initial_deposits').help_text,
        validators=[make_json_list_validator('initial_deposits', InitialDepositsSerializer)])
    retirement_postal_code = serializers.CharField(max_length=10, required=False)

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

        )

    def __init__(self, *args, **kwargs):
        super(RetirementPlanWritableSerializer, self).__init__(*args, **kwargs)

        # request-based validation
        request = self.context.get('request')
        if request.method == 'PUT':
            for field in self.fields.values():
                field.required = False

    @transaction.atomic
    def create(self, validated_data):
        client = validated_data['client']
        if not validated_data.get('retirement_postal_code', ''):
            if validated_data['same_home'] or validated_data['same_location']:
                postal_code = client.residential_address.post_code
                validated_data['retirement_postal_code'] = postal_code
            else:
                raise ValidationError('retirement_postal_code required if not same_home and not same_location')

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
