from rest_framework import serializers

from main.models import Goal, ClientAccount


__all__ = (
    'GoalSerializer', 'GoalListSerializer',
    'GoalUpdateSerializer',
)


class GoalClientAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientAccount
        #exclude = (
        #    'id',
        #)


class GoalSerializer(serializers.ModelSerializer):
    client_account = GoalClientAccountSerializer()

    class Meta:
        model = Goal


class GoalListSerializer(serializers.ModelSerializer):
    """
    Light version of GoalSerializer
    """
    class Meta:
        model = Goal
        exclude = (
            #'data', 'description',
            #'created_at', 'updated_at',
        )


class GoalUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Goal
        fields = (
            'target', 'portfolio',
        ) # list fields explicitly

    def __init__(self, *args, **kwargs):
        super(GoalUpdateSerializer, self).__init__(*args, **kwargs)

        # request based validation
        request = self.context.get('request')
        if not request:
            return # for swagger's dummy calls only

        #user = request.user

        # experimental / for advisors only
        #if user.is_advisor:
        #    self.fields['account'].queryset = \
        #        self.fields['account'].queryset.filter_by_advisor(user.advisor)
        #    self.fields['portfolio'].queryset = \
        #        self.fields['portfolio'].queryset.filter_by_advisor(user.advisor)

