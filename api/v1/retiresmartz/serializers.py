from datetime import date
from django.conf import settings
from django.db import transaction
from django.utils.timezone import now

from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied, ValidationError

from api.v1.serializers import ReadOnlyModelSerializer
from retiresmartz.models import RetirementPlan, RetirementPlanBTC, RetirementPlanATC
from client.models import Client
import json


def get_default_tx_plan():
    return {
        'begin_date': now().today().date(),
        'amount': 0,
        'growth': settings.BETASMARTZ_CPI,
        'schedule': 'RRULE:FREQ=MONTHLY;BYMONTHDAY=1'
    }


def get_default_life_expectancy(client):
    return settings.MALE_LIFE_EXPECTANCY if client.gender == 'Male' else settings.FEMALE_LIFE_EXPECTANCY


def get_default_retirement_date(client):
    return date(client.date_of_birth.year + 67, client.date_of_birth.month, client.date_of_birth.day)


class BTCSerializer(ReadOnlyModelSerializer):
    class Meta:
        model = RetirementPlanBTC
        exclude = ('plan',)


class ATCSerializer(ReadOnlyModelSerializer):
    class Meta:
        model = RetirementPlanATC
        exclude = ('plan',)

def who_validator(value):
    if value not in ['self', 'partner', 'joint']:
        raise ValidationError("'who' must be (self|partner|joint)")

def make_category_validator(category):
    def category_validator(value):
        if not value in category:
            raise ValidationError("'cat' for %s must be one of %s"%(category, category.choices()))

def make_json_list_validator(field, serializer):
    def list_item_validator(value):
        try: value = json.loads(value)
        except ValueError: raise ValidationError("Invalid json for %s"%field)
        if not isinstance(value, list):
            raise ValidationError("%s must be a JSON list of objects"%(field))
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


class BTCWritableSerializer(serializers.ModelSerializer):
    class Meta:
        model = RetirementPlanBTC
        fields = (
            'begin_date',
            'amount',
            'growth',
            'schedule',
        )


class ATCWritableSerializer(serializers.ModelSerializer):
    class Meta:
        model = RetirementPlanATC
        fields = (
            'begin_date',
            'amount',
            'growth',
            'schedule',
        )

class RetirementPlanSerializer(ReadOnlyModelSerializer):
    btc = BTCSerializer()
    atc = ATCSerializer()

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
    #savings = SavingsWritableSerializer(required=False)
    #initial_deposits = InitialDepositsWritableSerializer(required=False)
    btc = BTCWritableSerializer(required=False)
    atc = ATCWritableSerializer(required=False)

    class Meta:
        model = RetirementPlan
        fields = (
            'name',
            'description',
            'partner_plan',
            'smsf_account',
            'lifestyle',
            'desired_income',
            'current_income',
            'volunteer_days',
            'paid_days',
            'same_home',
            'retirement_postal_code',
            'reverse_mortgage',
            'retirement_home_style',
            'retirement_home_price',
            'beta_spouse',
            'expenses',
            'savings',
            'initial_deposits',
            'income_growth',
            'expected_return_confidence',
            'retirement_age',

            'btc',
            'atc',

            'max_match',
            'desired_risk',
            'recommended_risk',
            'max_risk',
            'calculated_life_expectancy',
            'selected_life_expectancy',

            'portfolio',
            'partner_data',

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
        btc = validated_data.pop('btc', None) or get_default_tx_plan()
        atc = validated_data.pop('atc', None) or get_default_tx_plan()
        client = validated_data['client']

        plan = RetirementPlan.objects.create(**validated_data)

        ser = BTCWritableSerializer(data=btc)
        ser.is_valid(raise_exception=True)
        ser.save(plan=plan)

        ser = ATCWritableSerializer(data=atc)
        ser.is_valid(raise_exception=True)
        ser.save(plan=plan)

        return plan

    @transaction.atomic
    def update(self, instance, validated_data):
        """
        Override the default update because we have nested relations.
        :param instance:
        :param validated_data:
        :return: The updated RetirementPlan
        """

        btc = validated_data.pop('btc', None)
        atc = validated_data.pop('atc', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        reverse_plan = getattr(instance, 'partner_plan_reverse', None)
        if instance.partner_plan is not None and reverse_plan is not None and instance.partner_plan != reverse_plan:
            emsg = "Partner plan relationship must be symmetric. " \
                   "I.e. Your selected partner plan must have you as it's partner"
            raise ValidationError(emsg)

        instance.save()

        if btc:
            if instance.btc is not None:
                instance.btc.delete()
            ser = BTCWritableSerializer(data=btc)
            ser.is_valid(raise_exception=True)
            ser.save(plan=instance)
        if atc:
            if instance.atc is not None:
                instance.atc.delete()
            ser = ATCWritableSerializer(data=atc)
            ser.is_valid(raise_exception=True)
            ser.save(plan=instance)

        return instance
