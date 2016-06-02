from django.db import models
from django.contrib.auth.models import Group # User
from django.apps import apps

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


@property
def is_advisor(self):
    """
    Custom helper method for User class to check user type/profile.
    """
    if not hasattr(self, '_is_advisor'):
        self._is_advisor = self.groups.filter(name=User.GROUP_ADVISOR).exists()

    return self._is_advisor


@property
def is_authorized_representative(self):
    """
    Custom helper method for User class to check user type/profile.
    """
    if not hasattr(self, '_is_authorized_representative'):
        self._is_authorized_representative = self.groups.filter(
            name=User.GROUP_AUTHORIZED_REPRESENTATIVE).exists()

    return self._is_authorized_representative


@property
def is_supervisor(self):
    """
    Custom helper method for User class to check user type/profile.
    """
    if not hasattr(self, '_is_supervisor'):
        self._is_supervisor = self.groups.filter(name=User.GROUP_SUPERVISOR).exists()

    return self._is_supervisor


@property
def is_client(self):
    """
    Custom helper method for User class to check user type/profile.
    """
    if not hasattr(self, '_is_client'):
        self._is_client = self.groups.filter(name=User.GROUP_CLIENT).exists()

    return self._is_client


# Add custom methods to User class
User.add_to_class('groups_add', groups_add)
User.add_to_class('groups_remove', groups_remove)

User.add_to_class('is_advisor', is_advisor)
User.add_to_class('is_authorized_representative', is_authorized_representative)
User.add_to_class('is_supervisor', is_supervisor)
User.add_to_class('is_client', is_client)

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


from . import connectors # just to init all the connectors, don't remove it
