from django.db.models.signals import m2m_changed
from django.contrib.auth.models import User, Group
from django.dispatch import receiver
from django.apps import apps # for D1.8 to get model by name


@receiver(m2m_changed)
def create_profiles(sender, instance, model, pk_set, action, **kwargs):
    """
    Create profiles (Advisor, Client, ...)
    for user added to related groups
    """
    if isinstance(instance, Group) and issubclass(model, User):
        if action in ['post_add',]:
            group_name = instance.name
            profile_name = User.PROFILES.get(group_name)
            profile_cls = apps.get_model(**profile_name)

            if profile_cls:
                for pk in pk_set:
                    user = User.objects.get(pk=pk)
                    group_profile = profile_cls.objects.get_or_create(user=user)

    else:
        # it's not a m2m signal we are interested in
        return
