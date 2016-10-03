from django.contrib.auth.models import Group
from django.contrib.auth import hashers
from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _

from main.models import User # TODO: will be moved to the module


def groups_add(self, name):
    """
    Custom helper method for User class to add group(s).
    """
    group, _ = Group.objects.get_or_create(name=name)
    group.user_set.add(self)

    return self


def groups_remove(self, name):
    """
    Custom helper method for User class to remove group(s).
    """
    group, _ = Group.objects.get_or_create(name=name)
    group.user_set.remove(self)

    return self


# Add custom methods to User class
User.add_to_class('groups_add', groups_add)
User.add_to_class('groups_remove', groups_remove)

User.add_to_class('GROUP_ADVISOR', 'Advisors')
User.add_to_class('GROUP_AUTHORIZED_REPRESENTATIVE', 'AuthorizedRepresentatives') # TODO: would be nice to rename
User.add_to_class('GROUP_SUPERVISOR', 'Supervisors')
User.add_to_class('GROUP_CLIENT', 'Clients')


# TODO: update after modularization
User.add_to_class('PROFILES', {
    User.GROUP_ADVISOR: {'app_label': 'main', 'model_name': 'Advisor'},
    User.GROUP_AUTHORIZED_REPRESENTATIVE: {'app_label': 'main', 'model_name': 'AuthorisedRepresentative'},
    User.GROUP_SUPERVISOR: {'app_label': 'main', 'model_name': 'Supervisor'},
    User.GROUP_CLIENT: {'app_label': 'main', 'model_name': 'Client'},
    # add new profiles here
})


class SecurityQuestion(models.Model):
    """
    A Simple model to allow configuring a set of canned Security Questions
    """
    question = models.CharField(max_length=128, null=False, blank=False)

    def __str__(self):
        return _("%s") % self.question


class SecurityAnswer(models.Model):
    user = models.ForeignKey(User, db_index=True)
    # The question field is deliberately not a foreign key to the SecurityQuestion model because a user can create
    # their own questions if they desire.
    question = models.CharField(max_length=128, null=False, blank=False)
    # Answer is hashed using the same technique as passwords
    answer = models.CharField(max_length=128, null=False, blank=False)

    class Meta:
        unique_together = ('user', 'question')

    def __str__(self):
        return _("%s - %s") % (self.user, self.question)

    def hash_current_answer(self):
        self.set_answer(self.answer)

    def set_answer(self, raw_answer):
        if not bool(getattr(settings, "SECURITY_QUESTIONS_CASE_SENSITIVE", False)):
            raw_answer = raw_answer.upper()
        self.answer = hashers.make_password(raw_answer)

    def check_answer(self, raw_answer):
        if not bool(getattr(settings, "SECURITY_QUESTIONS_CASE_SENSITIVE", False)):
            raw_answer = raw_answer.upper()

        def setter(r_answer):
            self.set_answer(r_answer)
            self.save(update_fields=["answer"])
        return hashers.check_password(raw_answer, self.answer, setter)

    def set_unusable_answer(self):
        self.answer = hashers.make_password(None)

    def has_usable_answer(self):
        return hashers.is_password_usable(self.answer)

from . import connectors # just to init all the connectors, don't remove it
