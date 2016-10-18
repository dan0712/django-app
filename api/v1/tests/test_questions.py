# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from .factories import UserFactory, SecurityQuestionFactory, SecurityAnswerFactory


class SecurityQuestionsTests(APITestCase):
    def setUp(self):
        self.client = APIClient(enforce_csrf_checks=True)
        self.user = UserFactory.create()
        self.user2 = UserFactory.create()
        self.user3 = UserFactory.create()
        self.user4 = UserFactory.create()
        self.user5 = UserFactory.create()
        self.user6 = UserFactory.create()
        self.sa = SecurityAnswerFactory.create(user=self.user2)

        self.sa2 = SecurityAnswerFactory.create()

        self.sa3 = SecurityAnswerFactory.create(user=self.user2)
        self.sa4 = SecurityAnswerFactory.create(user=self.user5)
        self.sa5 = SecurityAnswerFactory.create(user=self.user6)

    def tearDown(self):
        self.client.logout()

    def test_get_questions(self):
        """
        Test that security questions list view returns
        canned security questions.
        """
        url = reverse('api:v1:canned-security-questions')
        number_of_questions = 3
        for x in range(number_of_questions):
            SecurityQuestionFactory.create()
        # unauthenticated requests
        response = self.client.get(url, {})
        self.assertEqual(response.status_code, status.HTTP_200_OK,
                         msg='200 for unauthenticated request to get canned security questions')

        self.client.force_authenticate(user=self.user)
        response = self.client.get(url, {})
        self.assertEqual(response.status_code, status.HTTP_200_OK,
                         msg='200 returned by authenticated request to get security questions')

        # check that number of security questions returned matches
        # how many we created
        self.assertEqual(len(response.data), number_of_questions,
                         msg='Number of questions in response data matches expectation')

        # and lets verify the number of questions increases accordingly
        more_questions = 2
        for x in range(more_questions):
            SecurityQuestionFactory.create()
        response = self.client.get(url, {})
        self.assertEqual(response.status_code, status.HTTP_200_OK,
                         msg='200 returned by authenticated request to get security questions')

        self.assertEqual(len(response.data), number_of_questions + more_questions,
                         msg='Number of questions in response data matches expectation')

    def test_get_question(self):
        """
        Test that the current authenticated user can
        retrieve their current security questions.
        """
        url = reverse('api:v1:user-security-question')
        # test unauthenticated raises 403
        response = self.client.get(url, {})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN,
                         msg='403 for unauthenticated request to get the users current security questions')

        self.client.force_authenticate(user=self.sa.user)
        response = self.client.get(url, {})
        self.assertEqual(response.status_code, status.HTTP_200_OK,
                         msg='200 returned by authenticated request to get the users current security question')

        # check that user's question is in the data
        self.assertTrue(self.sa.question in str(response.data),
                        msg='Make sure one of the questions is equal to the expected question')

        # make sure data count increments as expected here to validate it added the new question
        numbers_of_questions = len(response.data)

        # lets add a question and make sure it comes back to us
        q3 = SecurityAnswerFactory(user=self.sa.user)
        response = self.client.get(url, {})
        self.assertEqual(response.status_code, status.HTTP_200_OK,
                         msg='200 returned by authenticated request to get the users current security question')

        self.assertTrue(q3.question in str(response.data),
                        msg='Make sure one of the questions is equal to the expected question')

        self.assertTrue(numbers_of_questions + 1 == len(response.data))

    def test_set_question_answer(self):
        """
        Test that an authenticated user can set a new
        question and answer for their security answer.
        """
        url = reverse('api:v1:user-security-question')
        # default security answer is test
        new_question = 'Who is the Batman?'
        new_answer = 'Bruce Wayne'
        data = {
            'password': 'test',
            'question': new_question,
            'answer': new_answer,
        }
        # unauthenticated should 403
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN,
                         msg='403 for unauthenticated request to set security question')

        # good request should 200
        self.client.force_authenticate(user=self.sa.user)
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK,
                         msg='200 returned by authenticated request to set a new user security question and answer')

        # set existing question returns 409
        data['answer'] = 'This is a different answer for a pre-existing question'
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT,
                         msg='409 for authenticated request to set different answer on existing security question using new question endpoint')

        # 401 for wrong password to set new question
        data = {
            'password': 'wrong password',
            'question': 'some fancy new question',
            'answer': 'an easy answer',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED,
                         msg='401 returned by authenticated request to set a new user security question and answer with the wrong password')

    def test_update_security_answer(self):
        url = reverse('api:v1:user-security-question-update', args=[self.sa4.pk])
        new_question = 'a fancy new question'
        new_answer = 'new answer'
        data = {
            'old_answer': 'test',
            'question': new_question,
            'answer': new_answer,
        }

        # 403 for non-authenticated request
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN,
                         msg='403 for unauthenticated requests to update a security answer')

        self.client.force_authenticate(user=self.sa4.user)
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK,
                         msg='200 returned by correct authenticated request to check security answer')

        # check the new answer against the check answer endpoint
        check_url = reverse('api:v1:user-check-answer', args=[self.sa4.pk])
        data = {
            'answer': new_answer,
        }
        response = self.client.post(check_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK,
                         msg='200 returned by authenticated request to check answer with newly set answer')

        # 401 returned if old answer is wrong, lets grab a fresh user
        data = {
            'old_answer': 'this should just be test',
            'question': 'any new question',
            'answer': 'no one will guess this!',
        }
        self.client.force_authenticate(user=self.sa5.user)
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED,
                         msg='401 returned by authenticated request to check security answer with wrong old answer')

    def test_check_answer(self):
        url = reverse('api:v1:user-check-answer', args=[self.sa2.pk])
        # SecurityQuestionAnswerFactory default raw answers are test
        data = {
            'answer': 'test',
        }
        # check for 403 on an unauthenticated request first
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN,
                         msg='403 for unauthenticated requests to check security answer')

        self.client.force_authenticate(user=self.sa2.user)
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK,
                         msg='200 returned by correct authenticated request to check security answer')

        # check for 401 for wrong answers
        data = {
            'answer': 'This is the wrong answer',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED,
                         msg='401 returned by incorrect authenticated request to check security answer, wrong answer')

        # check for 401 for wrong question
        url = reverse('api:v1:user-check-answer', args=[self.sa3.pk])
        data = {
            'answer': 'test',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED,
                         msg='401 returned by incorrect authenticated request to check security answer, wrong question')

        # 404 for non-existant question check
        url = reverse('api:v1:user-check-answer', args=[999999])
        data = {
            'answer': 'test',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND,
                         msg='404 returned by authenticated request to check security answer, non existant question id')
