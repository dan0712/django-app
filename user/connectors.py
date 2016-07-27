from django.apps import apps  # for D1.8 to get model by name
from django.contrib.auth.models import User as DjangoUser, Group
from django.core.files.base import ContentFile
from django.db.models import signals
from django.dispatch import receiver

from main.models import User
from user.utils import generate_avatar


@receiver(signals.m2m_changed)
def create_profiles(sender, instance, model, pk_set, action, **kwargs):
    """
    Create profiles (Advisor, Client, ...)
    for user added to related groups
    """
    if isinstance(instance, Group) and issubclass(model, DjangoUser):
        if action in ['post_add', ]:
            group_name = instance.name
            profile_name = DjangoUser.PROFILES.get(group_name)
            profile_cls = apps.get_model(**profile_name)

            if profile_cls:
                for pk in pk_set:
                    user = DjangoUser.objects.get(pk=pk)
                    profile_cls.objects.get_or_create(user=user)

    else:
        # it's not a m2m signal we are interested in
        return


@receiver(signals.post_save, sender=User)
def create_avatar(sender: type, instance: User, **kwargs):
    if not instance.avatar:

        instance.avatar.save('avatar_%d' % instance.id,
                             ContentFile(generate_avatar(instance.email)))
