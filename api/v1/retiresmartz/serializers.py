from datetime import date
from django.conf import settings
from django.db import transaction
from django.utils.timezone import now

from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied, ValidationError

from api.v1.serializers import ReadOnlyModelSerializer
from main.models import RetirementPlan, RetirementPlanBTC, RetirementPlanEinc, RetirementPlanATC
from client.models import Client


def get_default_tx_plan():
    return {
        'begin_date': now().today(),
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


class EincSerializer(ReadOnlyModelSerializer):
    class Meta:
        model = RetirementPlanEinc
        exclude = ('plan',)


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


class EincWritableSerializer(serializers.ModelSerializer):
    class Meta:
        model = RetirementPlanEinc
        fields = (
            'begin_date',
            'amount',
            'growth',
            'schedule',
        )


class RetirementPlanSerializer(ReadOnlyModelSerializer):
    btc = BTCSerializer()
    atc = ATCSerializer()
    external_income = EincSerializer(many=True)

    class Meta:
        model = RetirementPlan


class RetirementPlanWritableSerializer(serializers.ModelSerializer):
    btc = BTCWritableSerializer(required=False)
    atc = ATCWritableSerializer(required=False)
    external_income = EincWritableSerializer(required=False, many=True)
    life_expectancy = serializers.IntegerField(required=False)
    retirement_date = serializers.DateField(required=False)

    class Meta:
        model = RetirementPlan
        fields = (
            'name',
            'description',
            'partner_plan',
            'retirement_date',
            'life_expectancy',
            'spendable_income',
            'btc',
            'atc',
            'external_income',
            'desired_income',
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
        einc = validated_data.pop('external_income', None)
        client = validated_data['client']

        if 'life_expectancy' not in validated_data:
            validated_data['life_expectancy'] = get_default_life_expectancy(client)
        if 'retirement_date' not in validated_data:
            validated_data['retirement_date'] = get_default_retirement_date(client)

        plan = RetirementPlan.objects.create(**validated_data)

        ser = BTCWritableSerializer(data=btc)
        ser.is_valid(raise_exception=True)
        ser.save(plan=plan)

        ser = ATCWritableSerializer(data=atc)
        ser.is_valid(raise_exception=True)
        ser.save(plan=plan)

        if einc is not None:
            ser = EincWritableSerializer(data=einc, many=True)
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
        einc = validated_data.pop('external_income', None)

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
        if einc:
            if instance.external_income is not None:
                instance.external_income.all().delete()
            ser = EincWritableSerializer(data=einc, many=True)
            ser.is_valid(raise_exception=True)
            ser.save(plan=instance)

        return instance
