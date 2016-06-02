from django.dispatch import receiver
from django.db.models.signals import post_save, pre_save, post_delete
from django.contrib.auth.signals import user_logged_in, user_logged_out # TODO: experimental
from notifications.signals import notify

from main.models import Client


@receiver(post_save, sender=Client)
def client__post_save__group(sender, instance, created, **kwargs):
    """
    Experimental
    Add user to Client group on profile creation
    (maybe it could be done from other end)
    """
    if created and isinstance(instance, Client):
        user = instance.user
        user.groups_add(user.GROUP_CLIENT)


@receiver(user_logged_in)
def client__user_logged_in__test(sender, user, request, **kwargs):
    if user and user.is_client:
        # actor is always user object
        notify.send(user, recipient=user, verb='login')


@receiver(user_logged_out)
def client__user_logged_out__test(sender, user, request, **kwargs):
    if user and user.is_client:
        # actor is always user object
        notify.send(user, recipient=user, verb='logout')
