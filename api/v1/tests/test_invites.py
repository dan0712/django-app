import os
import json
from datetime import date
from django.conf import settings
from django.core.urlresolvers import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core import mail
from rest_framework import status
from rest_framework.test import APITestCase
from django.test import Client as DjangoClient
from common.constants import GROUP_SUPPORT_STAFF
from main.constants import ACCOUNT_TYPE_PERSONAL
from .factories import AdvisorFactory, SecurityQuestionFactory, EmailInviteFactory
from .factories import AccountTypeRiskProfileGroupFactory, AddressFactory, \
    ClientAccountFactory, ClientFactory, GroupFactory, RegionFactory, RiskProfileGroupFactory
from client.models import EmailInvite
from main.constants import EMPLOYMENT_STATUS_FULL_TIME, GENDER_MALE


class InviteTests(APITestCase):
    def setUp(self):
        self.maxDiff = None
        self.support_group = GroupFactory(name=GROUP_SUPPORT_STAFF)
        # client with some personal assets, cash balance and goals
        self.region = RegionFactory.create()
        self.betasmartz_client_address = AddressFactory(region=self.region)
        self.risk_group = RiskProfileGroupFactory.create(name='Personal Risk Profile Group')
        self.personal_account_type = AccountTypeRiskProfileGroupFactory.create(account_type=ACCOUNT_TYPE_PERSONAL,
                                                                               risk_profile_group=self.risk_group)
        self.advisor = AdvisorFactory.create()
        self.question_one = SecurityQuestionFactory.create()
        self.question_two = SecurityQuestionFactory.create()

    def tearDown(self):
        self.client.logout()

    def test_register_clears_sensitive_onboarding_login_data_from_EmailInvite(self):
        # check to make sure sensitive information isn't stored in onboarding_data
        # since user is registered now
        invite = EmailInviteFactory.create(status=EmailInvite.STATUS_SENT)
        onboarding = '{"risk":{"steps":[{"completed":false}],"completed":false},"agreements":{"steps":[{"advisorAgreement":false,\
          "betasmartzAgreement":false,"completed":false}],"completed":false},\
          "info":{"steps":[{"completed":false},{"completed":false},{"completed":false},{"completed":false}],"completed":false}, \
          "login":{"steps":[{"primarySecurityQuestion":"What was the name of your elementary school?","password":"t47LLRtur7O*PI", \
                "primarySecurityAnswer":"1","passwordConfirmation":"t47LLRtur7O*PI","secondarySecurityAnswer":"None",\
                "secondarySecurityQuestion":"What was the name of your favorite childhood friend?"}],"completed":true}}'
        invite.onboarding_data = json.loads(onboarding)
        invite.save()
        url = reverse('api:v1:client-user-register')
        data = {
            'first_name': invite.first_name,
            'last_name': invite.last_name,
            'invite_key': invite.invite_key,
            'password': 'test',
            'question_one': 'what is the first answer?',
            'question_one_answer': 'answer one',
            'question_two': 'what is the second answer?',
            'question_two_answer': 'answer two',
        }
        response = self.client.post(url, dict(data, question_one=''))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST,
                         msg='400 on bad question')
        response = self.client.post(url, dict(data, question_two=''))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST,
                         msg='400 on bad question')
        response = self.client.post(url, dict(data, question_one_answer=''))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST,
                         msg='400 on bad question answer')
        response = self.client.post(url, dict(data, question_two_answer=''))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST,
                         msg='400 on bad question answer')

        # With a valid token, get a valid user
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK,
                         msg='Register a valid invitation is 200 OK')
        self.assertNotEqual(response.data['id'], None,
                            msg='Registering an invitation should give valid user_id')
        self.assertEqual(response.data['email'], invite.email)

        lookup_invite = EmailInvite.objects.get(pk=invite.pk)
        self.assertEqual(response.data['email'], invite.email,
                         msg='New users email should match invitation')
        self.assertEqual(response.data['id'], lookup_invite.user.id,
                         msg='New users id should match invitation')
        self.assertEqual(EmailInvite.STATUS_ACCEPTED, lookup_invite.status)
        self.assertEqual(lookup_invite.onboarding_data['login']['steps'][0]['password'], '')
        self.assertEqual(lookup_invite.onboarding_data['login']['steps'][0]['passwordConfirmation'], '')
        self.assertEqual(lookup_invite.onboarding_data['login']['steps'][0]['primarySecurityQuestion'], '')
        self.assertEqual(lookup_invite.onboarding_data['login']['steps'][0]['primarySecurityAnswer'], '')
        self.assertEqual(lookup_invite.onboarding_data['login']['steps'][0]['secondarySecurityQuestion'], '')
        self.assertEqual(lookup_invite.onboarding_data['login']['steps'][0]['secondarySecurityAnswer'], '')

    def test_register_answers_validate(self):
        invite = EmailInviteFactory.create(status=EmailInvite.STATUS_SENT)

        url = reverse('api:v1:client-user-register')
        data = {
            'first_name': invite.first_name,
            'last_name': invite.last_name,
            'invite_key': invite.invite_key,
            'password': 'test',
            'question_one': 'what is the first answer?',
            'question_one_answer': 'answer one',
            'question_two': 'what is the second answer?',
            'question_two_answer': 'answer two',
        }

        # 400 no such token=123
        response = self.client.post(url, dict(data, invite_key='123'))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST,
                         msg='400 for registrations from nonexistant email invite')

        # 400 on bad securityquestions
        response = self.client.post(url, dict(data, question_one=''))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST,
                         msg='400 on bad question')
        response = self.client.post(url, dict(data, question_two=''))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST,
                         msg='400 on bad question')
        response = self.client.post(url, dict(data, question_one_answer=''))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST,
                         msg='400 on bad question answer')
        response = self.client.post(url, dict(data, question_two_answer=''))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST,
                         msg='400 on bad question answer')

        # With a valid token, get a valid user
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK,
                         msg='Register a valid invitation is 200 OK')
        self.assertNotEqual(response.data['id'], None,
                            msg='Registering an invitation should give valid user_id')
        self.assertEqual(response.data['email'], invite.email)

        lookup_invite = EmailInvite.objects.get(pk=invite.pk)
        self.assertEqual(response.data['email'], invite.email,
                         msg='New users email should match invitation')
        self.assertEqual(response.data['id'], lookup_invite.user.id,
                         msg='New users id should match invitation')
        self.assertEqual(EmailInvite.STATUS_ACCEPTED, lookup_invite.status)

        questions_url = reverse('api:v1:user-security-question')
        response = self.client.get(questions_url)
        test_question_id1 = response.data[0]['id']
        test_question_id2 = response.data[1]['id']
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        check_answer_url = reverse('api:v1:user-check-answer', args=[test_question_id1])
        # question/answer combo 1
        data = {
            'answer': 'answer one',
        }
        response = self.client.post(check_answer_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # question/answer combo 2
        check_answer_url = reverse('api:v1:user-check-answer', args=[test_question_id2])
        data = {
            'answer': 'answer two',
        }
        response = self.client.post(check_answer_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_register_with_invite_key(self):
        # Bring an invite key, get logged in as a new user
        invite = EmailInviteFactory.create(status=EmailInvite.STATUS_SENT)

        url = reverse('api:v1:client-user-register')
        data = {
            'first_name': invite.first_name,
            'last_name': invite.last_name,
            'invite_key': invite.invite_key,
            'password': 'test',
            'question_one': 'what is the first answer?',
            'question_one_answer': 'answer one',
            'question_two': 'what is the second answer?',
            'question_two_answer': 'answer two',
        }

        # 400 no such token=123
        response = self.client.post(url, dict(data, invite_key='123'))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST,
                         msg='400 for registrations from nonexistant email invite')

        # 400 on bad securityquestions
        response = self.client.post(url, dict(data, question_one=''))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST,
                         msg='400 on bad question')
        response = self.client.post(url, dict(data, question_two=''))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST,
                         msg='400 on bad question')
        response = self.client.post(url, dict(data, question_one_answer=''))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST,
                         msg='400 on bad question answer')
        response = self.client.post(url, dict(data, question_two_answer=''))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST,
                         msg='400 on bad question answer')

        # With a valid token, get a valid user
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK,
                         msg='Register a valid invitation is 200 OK')
        self.assertNotEqual(response.data['id'], None,
                            msg='Registering an invitation should give valid user_id')
        self.assertEqual(response.data['email'], invite.email)

        lookup_invite = EmailInvite.objects.get(pk=invite.pk)
        self.assertEqual(response.data['email'], invite.email,
                         msg='New users email should match invitation')
        self.assertEqual(response.data['id'], lookup_invite.user.id,
                         msg='New users id should match invitation')
        self.assertEqual(EmailInvite.STATUS_ACCEPTED, lookup_invite.status)


        # New user must be logged in too
        self.assertIn('sessionid', response.cookies)

        # We should have notified the advisor
        self.assertEqual(mail.outbox[0].subject, 'Client has accepted your invitation',
                         msg='Email outbox has email with expected subject')

        # Make sure /api/v1/me has invitation info
        response = self.client.get(reverse('api:v1:user-me'))
        self.assertEqual(response.status_code, status.HTTP_200_OK,
                         msg='/api/v1/me should be valid during invitation')
        self.assertEqual(response.data['invitation']['invite_key'], invite.invite_key,
                         msg='/api/v1/me should have invitation data')
        self.assertEqual(response.data['invitation']['status'],
                         EmailInvite.STATUS_ACCEPTED,
                         msg='/api/v1/me should have invitation status ACCEPTED')

        # GET: /api/v1/invites/:key
        # If a session is not logged in, return 200 with data
        self.client.logout()

        response = self.client.get(reverse('api:v1:invite-detail',
                                           kwargs={'invite_key': invite.invite_key} ))
        self.assertEqual(response.status_code, status.HTTP_200_OK,
                         msg='/api/v1/invites/:key should be valid during invitation')
        self.assertEqual(response.data['invite_key'], invite.invite_key,
                         msg='/api/v1/invites/:key should have invitation data')
        self.assertEqual(response.data['status'], EmailInvite.STATUS_ACCEPTED,
                         msg='/api/v1/invites/:key should have invitation status ACCEPTED')
        self.assertEqual('onboarding_data' in response.data, False,
                         msg='/api/v1/invites/:key should not show onboarding_data to anonymous')
        # verify firm data is present in response
        self.assertEqual(response.data['firm_logo'], lookup_invite.advisor.firm.logo.url)
        self.assertEqual(response.data['firm_colored_logo'], lookup_invite.advisor.firm.colored_logo)
        self.assertEqual(response.data['firm_name'], lookup_invite.advisor.firm.name)
        self.assertEqual(response.data['email'], lookup_invite.email)

    def test_register_logout_then_login(self):
        # Bring an invite key, get logged in as a new user
        PW = 'testpassword'
        invite = EmailInviteFactory.create(status=EmailInvite.STATUS_SENT)

        url = reverse('api:v1:client-user-register')
        data = {
            'first_name': invite.first_name,
            'last_name': invite.last_name,
            'invite_key': invite.invite_key,
            'password': PW,
            'question_one': 'what is the first answer?',
            'question_one_answer': 'answer one',
            'question_two': 'what is the second answer?',
            'question_two_answer': 'answer two',
        }

        # Accept an invitation and create a user
        response = self.client.post(url, data)
        lookup_invite = EmailInvite.objects.get(pk=invite.pk)
        invite_detail_url = reverse('api:v1:invite-detail', kwargs={'invite_key': invite.invite_key} )
        me_url = reverse('api:v1:user-me')
        self.assertEqual(EmailInvite.STATUS_ACCEPTED, lookup_invite.status)

        # New user must be logged in and able to see invite data
        self.assertIn('sessionid', response.cookies)
        response = self.client.get(me_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK,
                         msg='/api/v1/me should be valid during invitation')

        # If a session is not logged in, return 200 with data
        self.client.logout()
        response = self.client.get(me_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN,
                         msg='/api/v1/me denies unauthenticated user')

        # But this user can still log in again
        # through non-api url, user prob not using api to login
        # in this scenario
        # POST ing to the backup login url FAILS here:
        self.client = DjangoClient()  # django
        url = reverse('login')
        data = {
            'username': lookup_invite.user.email,
            'password': PW,
        }
        response = self.client.post(url, data)
        # redirects to frontend client onboarding
        self.assertRedirects(response, '/client/onboarding/' + lookup_invite.invite_key, fetch_redirect_response=False)
        self.assertIn('sessionid', response.cookies, msg='A user still onboarding can log in')

        response = self.client.get(me_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK,
                         msg='/api/v1/me works for newly authenticated user')

    def test_onboard_after_register(self):
        # Bring an invite key, get logged in as a new user
        invite = EmailInviteFactory.create(status=EmailInvite.STATUS_SENT)

        url = reverse('api:v1:client-user-register')
        data = {
            'first_name': invite.first_name,
            'last_name': invite.last_name,
            'invite_key': invite.invite_key,
            'password': 'test',
            'question_one': 'what is the first answer?',
            'question_one_answer': 'answer one',
            'question_two': 'what is the second answer?',
            'question_two_answer': 'answer two',
        }

        # Accept an invitation and create a user
        response = self.client.post(url, data)
        lookup_invite = EmailInvite.objects.get(pk=invite.pk)
        invite_detail_url = reverse('api:v1:invite-detail', kwargs={'invite_key': invite.invite_key} )

        self.assertEqual(EmailInvite.STATUS_ACCEPTED, lookup_invite.status)

        # New user must be logged in too
        self.assertIn('sessionid', response.cookies)

        # GET: /api/v1/invites/:key
        # If a session is logged in, return 200 with data
        response = self.client.get(invite_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK,
                         msg='/api/v1/invites/:key should be valid during invitation')
        self.assertEqual(response.data['invite_key'], invite.invite_key,
                         msg='/api/v1/invites/:key should have invitation data')
        self.assertEqual(response.data['status'], EmailInvite.STATUS_ACCEPTED,
                         msg='/api/v1/invites/:key should have invitation status ACCEPTED')
        self.assertEqual('onboarding_data' in response.data, True,
                         msg='/api/v1/invites/:key should show onboarding_data to user')
        self.assertEqual(response.data['risk_profile_group'], self.risk_group.id)

        # Make sure the user now has access to the risk-profile-groups endpoint
        rpg_url = reverse('api:v1:settings-risk-profile-groups-list')
        response = self.client.get(rpg_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['id'], self.risk_group.id)

        # PUT: /api/v1/invites/:key
        # Submit with onboarding_data
        onboarding = {'onboarding_data': {'foo': 'bar'}}
        response = self.client.put(invite_detail_url, data=onboarding)

        lookup_invite = EmailInvite.objects.get(pk=invite.pk)
        self.assertEqual(response.status_code, status.HTTP_200_OK,
                         msg='Onboarding must accept json objects')
        self.assertEqual(response.data['status'], EmailInvite.STATUS_ACCEPTED,
                         msg='invitation status ACCEPTED')
        self.assertEqual(lookup_invite.onboarding_data['foo'], 'bar',
                         msg='should save onboarding_file')

        # PUT: /api/v1/invites/:key
        # Tax transcript upload and parsing
        expected_tax_transcript_data = {'SPOUSE NAME': 'SPOUSE M LAST', 'SPOUSE SSN': '222-22-2222', 'ADDRESS': '999 AVENUE RD  CITY, ST 10.000-90.00-800', 'NAME': 'FIRST M', 'SSN': '111-11-1111', 'FILING STATUS': 'Married Filing Joint', 'TOTAL INCOME': '$0.00'}
        with open(os.path.join(settings.BASE_DIR, 'pdf_parsers', 'samples', 'sample.pdf'), mode="rb") as tax_transcript:
            data = {
                'tax_transcript': tax_transcript
            }
            response = self.client.put(invite_detail_url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_200_OK,
                         msg='Updating onboarding with tax_transcript PDF returns OK')
        self.assertNotEqual(response.data['tax_transcript_data'], None,
                            msg='tax_transcript_data is in the response and not None')
        self.assertEqual(response.data['tax_transcript_data'], expected_tax_transcript_data,
                         msg='Parsed tax_transcript_data matches expected')


        self.assertEqual(response._headers['content-type'], ('Content-Type', 'application/json'),
                         msg='Response content type is application/json after upload')

        lookup_invite = EmailInvite.objects.get(pk=invite.pk)
        self.assertEqual(response.data['status'], EmailInvite.STATUS_ACCEPTED,
                         msg='invitation status ACCEPTED')

        # create client and make sure tax_transcript data is carried over properly
        url = reverse('api:v1:client-list')
        address = {
            "address": "123 My Street\nSome City",
            "post_code": "112233",
            "region": {
                "name": "New South Wales",
                "country": "AU",
                "code": "NSW",
            }
        }
        regional_data = {
            'ssn': '555-55-5555',
            'politically_exposed': True,
        }
        data = {
            "advisor_agreement": True,
            "betasmartz_agreement": True,
            "date_of_birth": date(2016, 9, 21),
            "employment_status": EMPLOYMENT_STATUS_FULL_TIME,
            "gender": GENDER_MALE,
            "income": 1234,
            "phone_num": "+1-234-234-2342",
            "residential_address": address,
            "regional_data": json.dumps(regional_data)
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        regional_data_load = json.loads(response.data['regional_data'])
        self.assertNotEqual(regional_data_load['tax_transcript'], None)
        self.assertEqual(regional_data_load['tax_transcript_data']['FILING STATUS'],
                         expected_tax_transcript_data['FILING STATUS'],
                         msg='Parsed tax_transcript_data FILING STATUS parsed successfully')

    def test_complete_invitation(self):

        # Bring an invite key, get logged in as a new user
        invite = EmailInviteFactory.create(status=EmailInvite.STATUS_SENT,
                                           reason=EmailInvite.REASON_PERSONAL_INVESTING)

        url = reverse('api:v1:client-user-register')
        data = {
            'first_name': invite.first_name,
            'last_name': invite.last_name,
            'invite_key': invite.invite_key,
            'password': 'test',
            'question_one': 'what is the first answer?',
            'question_one_answer': 'answer one',
            'question_two': 'what is the second answer?',
            'question_two_answer': 'answer two',
        }

        # Accept an invitation and create a user
        response = self.client.post(url, data)
        invite = EmailInvite.objects.get(pk=invite.pk)
        user = invite.user
        invite_detail_url = reverse('api:v1:invite-detail', kwargs={'invite_key': invite.invite_key} )

        self.assertEqual(EmailInvite.STATUS_ACCEPTED, invite.status)

        # New user must be logged in too
        self.assertIn('sessionid', response.cookies)

        # PUT: /api/v1/invites/:key
        # Submit with onboarding_data
        onboarding = {'onboarding_data': json.dumps({'foo': 'bar'})}
        response = self.client.put(invite_detail_url, data=onboarding)
        self.assertEqual(response.status_code, status.HTTP_200_OK,
                         msg='Onboarding must accept json')

        betasmartz_client = ClientFactory.create(user=user)
        betasmartz_client_account = ClientAccountFactory(primary_owner=betasmartz_client, account_type=ACCOUNT_TYPE_PERSONAL, confirmed=False)
        betasmartz_client_account.confirmed = True
        betasmartz_client_account.save()

        invite = EmailInvite.objects.get(pk=invite.pk)
        self.assertEqual(invite.onboarding_data, None)
        self.assertEqual(invite.status, EmailInvite.STATUS_COMPLETE)

    def test_resend_client_invite(self):
        """
        Allow authenticated users to resend email invites for onboarding
        """
        invite = EmailInviteFactory.create(status=EmailInvite.STATUS_SENT,
                                           reason=EmailInvite.REASON_PERSONAL_INVESTING)
        url = reverse('api:v1:client-user-register')
        data = {
            'first_name': invite.first_name,
            'last_name': invite.last_name,
            'invite_key': invite.invite_key,
            'password': 'test',
            'question_one': 'what is the first answer?',
            'question_one_answer': 'answer one',
            'question_two': 'what is the second answer?',
            'question_two_answer': 'answer two',
        }

        # Accept an invitation and create a user
        response = self.client.post(url, data)
        invite = EmailInvite.objects.get(pk=invite.pk)

        self.client.logout()
        url = reverse('api:v1:resend-invite', args=[invite.pk])
        response = self.client.post(url, {})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.client.force_authenticate(invite.user)
        response = self.client.post(url, {})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(mail.outbox[-1].subject, 'BetaSmartz client sign up form url',
                         msg='Email outbox has email with expected resend email subject')
        lookup_invite = EmailInvite.objects.get(pk=invite.pk)
        self.assertEqual(lookup_invite.send_count, 1)
