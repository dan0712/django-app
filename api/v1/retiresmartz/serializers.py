import datetime

from django.conf import settings
from django.db import transaction

from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied, ValidationError

from api.v1.serializers import ReadOnlyModelSerializer, NoUpdateModelSerializer, NoCreateModelSerializer
from main.models import RetirementPlan, TransferPlan, Client


def get_default_tx_plan():
    return {
        'begin_date': datetime.date.today(),
        'amount': 0,
        'growth': settings.BETASMARTZ_CPI,
        'schedule': 'RRULE:FREQ=MONTHLY;BYMONTHDAY=1'
    }


def get_default_life_expectancy(client):
    return settings.MALE_LIFE_EXPECTANCY if client.gender == 'Male' else settings.FEMALE_LIFE_EXPECTANCY


def get_default_retirement_date(client):
    return datetime.date(client.date_of_birth.year + 67, client.date_of_birth.month, client.date_of_birth.day)


class TransferPlanSerializer(ReadOnlyModelSerializer):
    class Meta:
        model = TransferPlan


class TransferPlanWritableSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransferPlan
        fields = (
            'begin_date',
            'amount',
            'growth',
            'schedule',
        )


class RetirementPlanSerializer(ReadOnlyModelSerializer):
    btc = TransferPlanSerializer()
    atc = TransferPlanSerializer()
    class Meta:
        model = RetirementPlan


class RetirementPlanCreateSerializer(NoUpdateModelSerializer):
    btc = TransferPlanWritableSerializer(required=False)
    atc = TransferPlanWritableSerializer(required=False)
    life_expectancy = serializers.IntegerField(required=False)
    retirement_date = serializers.DateField(required=False)

    class Meta:
        model = RetirementPlan
        fields = (
            'name',
            'description',
            'client',
            'partner_plan',
            'retirement_date',
            'life_expectancy',
            'spendable_income',
            'btc',
            'atc',
            'desired_income',
        )

    def __init__(self, *args, **kwargs):
        super(RetirementPlanCreateSerializer, self).__init__(*args, **kwargs)

        # request-based validation
        request = self.context.get('request')
        user = request.user

        if user.is_client:
            self.fields['client'].required = False
            self.fields['client'].default = user.client

    @transaction.atomic
    def create(self, validated_data):
        """
        Override the default create because we need to check permissions for the user against the client in the request
        data.
        :param validated_data:
        :return: The created RetirementPlan
        """
        request = self.context.get('request')
        client = Client.objects.filter_by_user(request.user).filter(pk=validated_data['client'].pk).first()
        if not client:
            return PermissionDenied("Not authorised for Client: {}".format(validated_data['client']))

        if 'btc' not in validated_data:
            validated_data['btc'] = get_default_tx_plan()
        if 'atc' not in validated_data:
            validated_data['atc'] = get_default_tx_plan()
        if 'life_expectancy' not in validated_data:
            validated_data['life_expectancy'] = get_default_life_expectancy(client)
        if 'retirement_date' not in validated_data:
            validated_data['retirement_date'] = get_default_retirement_date(client)

        ser = TransferPlanWritableSerializer(data=validated_data['btc'])
        ser.is_valid(raise_exception=True)
        validated_data['btc'] = ser.save()

        ser = TransferPlanWritableSerializer(data=validated_data['atc'])
        ser.is_valid(raise_exception=True)
        validated_data['atc'] = ser.save()

        return RetirementPlan.objects.create(**validated_data)


class RetirementPlanUpdateSerializer(NoCreateModelSerializer):
    btc = TransferPlanWritableSerializer()
    atc = TransferPlanWritableSerializer()

    class Meta:
        model = RetirementPlan
        fields = (
            'name',
            'description',
            'client',
            'partner_plan',
            'retirement_date',
            'life_expectancy',
            'spendable_income',
            'btc',
            'atc',
            'desired_income',
        )

    def __init__(self, *args, **kwargs):
        """
        Override init to enable partial updates
        :param args:
        :param kwargs:
        """
        kwargs.pop('partial', None)
        super(RetirementPlanUpdateSerializer, self).__init__(*args, partial=True, **kwargs)

    @transaction.atomic
    def update(self, instance, validated_data):
        """
        Override the default update because we have nested relations.
        :param instance:
        :param validated_data:
        :return: The updated RetirementPlan
        """
        btc = validated_data.pop('btc', None)
        if btc:
            ser = TransferPlanWritableSerializer(data=btc)
            ser.is_valid(raise_exception=True)
            instance.btc = ser.save()

        atc = validated_data.pop('atc', None)
        if atc:
            ser = TransferPlanWritableSerializer(data=atc)
            ser.is_valid(raise_exception=True)
            instance.atc = ser.save()

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        reverse_plan = getattr(instance, 'partner_plan_reverse', None)
        if instance.partner_plan is not None and reverse_plan is not None and instance.partner_plan != reverse_plan:
            emsg = "Partner plan relationship must be symmetric. " \
                   "I.e. Your selected partner plan must have you as it's partner"
            raise ValidationError(emsg)

        instance.save()
        return instance
