from django.contrib.auth import authenticate, login as auth_login
from rest_framework import viewsets, views, mixins
from rest_framework import exceptions, parsers, status
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.viewsets import GenericViewSet
from rest_framework_extensions.mixins import NestedViewSetMixin
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from api.v1.client.serializers import EmailNotificationsSerializer, \
    PersonalInfoSerializer
from api.v1.permissions import IsClient
from api.v1.views import ApiViewMixin
from main.models import ExternalAsset, User
from user.models import SecurityAnswer
from client.models import Client, EmailInvite
from support.models import SupportRequest
from api.v1.user.serializers import UserSerializer
from api.v1.retiresmartz.serializers import RetirementPlanEincSerializer, RetirementPlanEincWritableSerializer
from retiresmartz.models import RetirementPlan, RetirementPlanEinc, RetirementAdvice
from django.views.generic.detail import SingleObjectMixin
from . import serializers
import logging
import json
from retiresmartz import advice_responses
from main.event import Event

logger = logging.getLogger('api.v1.client.views')


class ExternalAssetViewSet(ApiViewMixin, NestedViewSetMixin, viewsets.ModelViewSet):
    model = ExternalAsset
    # We define the queryset because our get_queryset calls super so the Nested queryset works.
    queryset = ExternalAsset.objects.all()
    serializer_class = serializers.ExternalAssetSerializer
    pagination_class = None

    # Set the response serializer because we want to use the 'get' serializer for responses from the 'create' methods.
    # See api/v1/views.py
    serializer_response_class = serializers.ExternalAssetSerializer

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'POST']:
            return serializers.ExternalAssetWritableSerializer
        else:
            # Default for get and other requests is the read only serializer
            return serializers.ExternalAssetSerializer

    def get_queryset(self):
        qs = super(ExternalAssetViewSet, self).get_queryset()

        # Only return assets which the user has access to.
        user = SupportRequest.target_user(self.request)
        return qs.filter_by_user(user)


class RetirementIncomeViewSet(ApiViewMixin, NestedViewSetMixin, viewsets.ModelViewSet):
    model = RetirementPlanEinc
    # We define the queryset because our get_queryset calls super so the Nested queryset works.
    queryset = RetirementPlanEinc.objects.all()
    serializer_class = RetirementPlanEincSerializer
    pagination_class = None

    # Set the response serializer because we want to use the 'get' serializer for responses from the 'create' methods.
    # See api/v1/views.py
    serializer_response_class = RetirementPlanEincSerializer

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'POST']:
            return RetirementPlanEincWritableSerializer
        else:
            # Default for get and other requests is the read only serializer
            return RetirementPlanEincSerializer

    def get_queryset(self):
        qs = super(RetirementIncomeViewSet, self).get_queryset()

        # Only return assets which the user has access to.
        user = SupportRequest.target_user(self.request)
        allow_plans = RetirementPlan.objects.filter_by_user(user)
        return qs.filter(plan__in=allow_plans)


class ClientViewSet(ApiViewMixin,
                    NestedViewSetMixin,
                    mixins.CreateModelMixin,
                    mixins.RetrieveModelMixin,
                    mixins.UpdateModelMixin,
                    mixins.ListModelMixin,
                    GenericViewSet):
    """
    Everything except delete
    """
    model = Client
    # We define the queryset because our get_queryset calls super so the Nested queryset works.
    queryset = Client.objects.all()
    serializer_class = serializers.ClientSerializer
    # Set the response serializer because we want to use the 'get' serializer for responses from the 'create' methods.
    # See api/v1/views.py
    serializer_response_class = serializers.ClientSerializer
    pagination_class = None

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'POST']:
            return serializers.ClientUpdateSerializer
        else:
            # Default for get and other requests is the read only serializer
            return serializers.ClientSerializer

    def get_queryset(self):
        qs = super(ClientViewSet, self).get_queryset()

        # Only return Clients the user has access to.
        user = SupportRequest.target_user(self.request)
        return qs.filter_by_user(user)

    def create(self, request, *args, **kwargs):
        if not hasattr(request.user, 'invitation') or EmailInvite.STATUS_ACCEPTED != getattr(request.user.invitation,
                                                                                             'status',
                                                                                             None):
            return Response({'error': 'requires account with accepted invitation'},
                            status=status.HTTP_405_METHOD_NOT_ALLOWED)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # creat new client
        client = serializer.save(advisor=request.user.invitation.advisor, user=request.user)
        if isinstance(client.regional_data, dict):
            rd = client.regional_data
        else:
            rd = json.loads(client.regional_data)
        if not rd.get('tax_transcript_data'):
            # add tax_transcript and tax_transcript_data from
            # the invitation serializer to client.regional_data
            invitation_serializer = serializers.PrivateInvitationSerializer(request.user.invitation)
            if invitation_serializer.data.get('tax_transcript', None) is not None:
                rd['tax_transcript'] = invitation_serializer.data.get('tax_transcript')
                rd['tax_transcript_data'] = invitation_serializer.data.get('tax_transcript_data')
                client.regional_data = json.dumps(rd)
                client.save()

        # set client invitation status to complete
        client.user.invitation.status = EmailInvite.STATUS_COMPLETE
        client.user.invitation.save()

        # Email the user "Welcome Aboard"
        self.request.user.email_user('Welcome to BetaSmartz!',
                                     "Congratulations! You've setup your first account, "
                                     "you're ready to start using BetaSmartz!")

        headers = self.get_success_headers(serializer.data)
        serializer = self.serializer_response_class(client)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        kwargs['partial'] = True
        partial = kwargs.pop('partial', False)
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        orig = Client.objects.get(pk=instance.pk)
        updated = serializer.update(instance, serializer.validated_data)

        # RetirementAdvice Triggers
        for plan in RetirementPlan.objects.filter(client=updated, agreed_on=None):
            life_expectancy_field_updated = (updated.daily_exercise != orig.daily_exercise or
                                             updated.weight != orig.weight or
                                             updated.height != orig.height or
                                             updated.smoker != orig.smoker or
                                             updated.drinks != orig.drinks)
            if updated.smoker != orig.smoker:
                if updated.smoker:
                    e = Event.RETIRESMARTZ_IS_A_SMOKER.log(None,
                                                           user=updated.user,
                                                           obj=updated)
                    advice = RetirementAdvice(plan=plan, trigger=e)
                    advice.text = advice_responses.get_smoking_yes(advice)
                    advice.save()
                elif updated.smoker is False:
                    e = Event.RETIRESMARTZ_IS_NOT_A_SMOKER.log(None,
                                                               user=updated.user,
                                                               obj=updated)
                    advice = RetirementAdvice(plan=plan, trigger=e)
                    advice.text = advice_responses.get_smoking_no(advice)
                    advice.save()
                    plan.selected_life_expectancy += 7
                    plan.save()

            if updated.daily_exercise != orig.daily_exercise:
                # exercise only
                e = Event.RETIRESMARTZ_EXERCISE_ONLY.log(None,
                                                         user=updated.user,
                                                         obj=updated)
                advice = RetirementAdvice(plan=plan, trigger=e)
                advice.text = advice_responses.get_exercise_only(advice)
                advice.save()

            # frontend posts one at a time, weight then height, not together in one post
            if (updated.weight != orig.weight or updated.height != orig.height):
                # weight and/or height updated
                e = Event.RETIRESMARTZ_WEIGHT_AND_HEIGHT_ONLY.log(None,
                                                                  user=updated.user,
                                                                  obj=updated)
                advice = RetirementAdvice(plan=plan, trigger=e)
                advice.text = advice_responses.get_weight_and_height_only(advice)
                advice.save()

            if life_expectancy_field_updated and (updated.daily_exercise and
               updated.weight and updated.height and updated.smoker is not None and
               updated.drinks is not None):
                # every wellbeing field
                e = Event.RETIRESMARTZ_ALL_WELLBEING_ENTRIES.log(None,
                                                                 user=updated.user,
                                                                 obj=updated)
                advice = RetirementAdvice(plan=plan, trigger=e)
                advice.text = advice_responses.get_all_wellbeing_entries(advice)
                advice.save()
        # elif life_expectancy_field_updated:
        #     # life expectancy field updated but not all of them
        #     # and not an individual one must be combination of
        #     # wellbeing entries updated
        #         e = Event.RETIRESMARTZ_COMBINATION_WELLBEING_ENTRIES.log(None,
        #                                                                  user=updated.user,
        #                                                                  obj=updated)
        #         advice = RetirementAdvice(plan=plan, trigger=e)
        #         advice.text = advice_responses.get_combination_of_more_than_one_entry_but_not_all(advice)
        #         advice.save()
        return Response(self.serializer_response_class(updated).data)


class InvitesView(ApiViewMixin, views.APIView):
    permission_classes = []
    serializer_class = serializers.PrivateInvitationSerializer
    parser_classes = (
        parsers.FormParser, parsers.MultiPartParser, parsers.JSONParser,
    )

    def get(self, request, invite_key):
        find_invite = EmailInvite.objects.filter(invite_key=invite_key)
        if not find_invite.exists:
            return Response({'error': 'invitation not found'}, status=status.HTTP_404_NOT_FOUND)

        invite = find_invite.get()

        if request.user.is_authenticated():
            # include onboarding data
            data = self.serializer_class(instance=invite).data
        else:
            data = serializers.InvitationSerializer(instance=invite).data
        return Response(data)

    def put(self, request, invite_key):
        if not request.user.is_authenticated():
            return Response({'error': 'not logged in'}, status=status.HTTP_401_UNAUTHORIZED)

        find_invite = EmailInvite.objects.filter(invite_key=invite_key)
        if not find_invite.exists:
            return Response({'error': 'invitation not found'}, status=status.HTTP_404_NOT_FOUND)

        invite = find_invite.get()

        if invite.status == EmailInvite.STATUS_EXPIRED:
            invite.advisor.user.email_user('A client tried to use an expired invitation'
                                           "Your potential client {} {} ({}) just tried to register using an invite "
                                           "you sent them, but it has expired!".format(invite.first_name,
                                                                                       invite.last_name,
                                                                                       invite.email))

        if invite.status != EmailInvite.STATUS_ACCEPTED:
            return Response(self.serializer_class(instance=invite).data,
                            status=status.HTTP_304_NOT_MODIFIED)

        serializer = self.serializer_class(invite, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()

        return Response(serializer.data)


class ClientUserRegisterView(ApiViewMixin, views.APIView):
    """
    Register Client's User from an invite token
    """
    permission_classes = []
    serializer_class = serializers.ClientUserRegistrationSerializer

    def post(self, request):
        serializer = serializers.ClientUserRegistrationSerializer(data=request.data)
        if not serializer.is_valid(raise_exception=True):
            logger.error('Error accepting invitation: %s' % serializer.errors['non_field_errors'][0])
            return Response({'error': 'invitation not found for this email'}, status=status.HTTP_404_NOT_FOUND)
        invite = serializer.invite

        user_params = {
            'email': invite.email,
            'username': invite.email,
            'first_name': invite.first_name,
            'last_name': invite.last_name,
            'password': serializer.validated_data['password'],
        }
        user = User.objects.create_user(**user_params)

        SecurityAnswer.objects.create(user=user,
                                      question=serializer.validated_data['question_one'],
                                      answer=serializer.validated_data['question_one_answer'])

        SecurityAnswer.objects.create(user=user,
                                      question=serializer.validated_data['question_two'],
                                      answer=serializer.validated_data['question_two_answer'])

        invite.status = EmailInvite.STATUS_ACCEPTED
        invite.user = user

        invite.save()

        login_params = {
            'username': user.email,
            'password': serializer.validated_data['password']
        }

        user = authenticate(**login_params)

        # check if user is authenticated
        if not user or not user.is_authenticated():
            raise exceptions.NotAuthenticated()

        # Log the user in with a session as well.
        auth_login(request, user)

        user_serializer = UserSerializer(instance=user)
        msg = "Your client %s %s (%s) has accepted your invitation to Betasmartz!" % (user.first_name,
                                                                                      user.last_name,
                                                                                      user.email)
        invite.advisor.user.email_user('Client has accepted your invitation', msg)
        return Response(user_serializer.data)


class EmailNotificationsView(ApiViewMixin, RetrieveUpdateAPIView):
    permission_classes = IsClient,
    serializer_class = EmailNotificationsSerializer

    def get_object(self):
        return Client.objects.get(user=self.request.user).notification_prefs


class ProfileView(ApiViewMixin, RetrieveUpdateAPIView):
    permission_classes = IsClient,
    serializer_class = PersonalInfoSerializer

    def get_object(self):
        return Client.objects.get(user=self.request.user)


class ClientResendInviteView(SingleObjectMixin, views.APIView):
    permission_classes = [IsAuthenticated, ]
    queryset = EmailInvite.objects.all()

    def post(self, request, *args, **kwargs):
        invite = self.get_object()
        if invite.user != self.request.user:
            return Response('forbidden', status=status.HTTP_403_FORBIDDEN)
        invite.send()
        return Response('ok', status=status.HTTP_200_OK)
