from django.dispatch import receiver
from django.db.models.signals import post_save, pre_save, post_delete
from django.contrib.auth.signals import user_logged_in, user_logged_out # TODO: experimental
from notifications.signals import notify

from main.models import Advisor, AuthorisedRepresentative, Supervisor

''' Commented as user has no groups_add method.
@receiver(post_save, sender=Advisor)
def advisor__post_save__group(sender, instance, created, **kwargs):
    """
    Experimental
    Add user to Advisor group on profile creation
    (maybe it could be done from other end)
    """
    if created:
        advisor = instance
        user = advisor.user
        user.groups_add(user.GROUP_ADVISOR)


@receiver(post_save, sender=Supervisor)
def supervisor__post_save__group(sender, instance, created, **kwargs):
    """
    Experimental
    Add user to Supervisor group on profile creation
    (maybe it could be done from other end)
    """
    if created:
        supervisor = instance
        user = supervisor.user
        user.groups_add(user.GROUP_SUPERVISOR)


@receiver(post_save, sender=AuthorisedRepresentative)
def authorized_representative__post_save__group(sender, instance, created, **kwargs):
    """
    Experimental
    Add user to Supervisor group on profile creation
    (maybe it could be done from other end)
    """
    if created:
        authorised_representative = instance
        user = authorised_representative.user
        user.groups_add(user.GROUP_AUTHORIZED_REPRESENTATIVE)
'''

@receiver(user_logged_in)
def advisor__user_logged_in__test(sender, user, request, **kwargs):
    if user and user.is_advisor:
        # actor is always user object
        notify.send(user, recipient=user, verb='login')


@receiver(user_logged_out)
def advisor__user_logged_out__test(sender, user, request, **kwargs):
    if user and user.is_advisor:
        # actor is always user object
        notify.send(user, recipient=user, verb='logout')
