from django.db import models
from django.contrib.auth.models import User, Group
from django.apps import apps


# RESERVED
#def groups_add(self, name):
#    """
#    Custom helper method for User class to add group(s).
#    """
#    group, _ = Group.objects.get_or_create(name=name)
#    group.user_set.add(self)
#
#    return self


# RESERVED
#def groups_remove(self, name):
#    """
#    Custom helper method for User class to remove group(s).
#    """
#    group, _ = Group.objects.get_or_create(name=name)
#    group.user_set.remove(self)
#
#    return self


@property
def is_advisor(self):
    """
    Custom helper method for User class to check user type/profile.
    """
    if not hasattr(self, '_is_advisor'):
        self._is_advisor = hasattr(self.user, 'advisor')
        #self._is_advisor = self.groups.filter(name=User.GROUP_ADVISOR).exists()

    return self._is_advisor


@property
def is_client(self):
    """
    Custom helper method for User class to check user type/profile.
    """
    if not hasattr(self, '_is_client'):
        self._is_advisor = hasattr(self.user, 'client')
        #self._is_client = self.groups.filter(name=User.GROUP_CLIENT).exists()

    return self._is_client


# Add custom methods to User class
#User.add_to_class('groups_add', groups_add)
#User.add_to_class('groups_remove', groups_remove)

User.add_to_class('is_advisor', is_advisor)
User.add_to_class('is_client', is_client)

#User.add_to_class('GROUP_ADVISOR', 'Advisors')
#User.add_to_class('GROUP_CLIENT', 'Clients')

#User.add_to_class('PROFILES', {
#    User.GROUP_ADVISOR: {'app_label': 'advisor', 'model_name': 'Advisor'},
#    User.GROUP_CLIENT: {'app_label': 'client', 'model_name': 'Client'},
#    # add new profiles here
#})
