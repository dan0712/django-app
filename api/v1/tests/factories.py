# -*- coding: utf-8 -*-
from main.models import User
import factory
from user.models import SecurityQuestion, SecurityAnswer


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    first_name = factory.Sequence(lambda n: 'Bruce%d' % n)
    last_name = factory.Sequence(lambda n: 'Wayne%d' % n)
    username = factory.Sequence(lambda n: 'user%d' % n)
    email = factory.LazyAttribute(lambda obj: '%s@example.com' % obj.username)
    password = factory.PostGenerationMethodCall('set_password', 'test')

    is_active = True


class StaffUserFactory(UserFactory):
    is_staff = True


class SuperUserFactory(UserFactory):
    is_superuser = True


class SecurityQuestionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = SecurityQuestion

    question = factory.Sequence(lambda n: 'Question %d' % n)


class SecurityAnswerFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = SecurityAnswer

    user = factory.SubFactory(UserFactory)
    question = factory.Sequence(lambda n: "Question %d" % n)
    answer = factory.PostGenerationMethodCall('set_answer', 'test')
