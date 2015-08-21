__author__ = 'cristian'

from django.contrib.auth.models import User


@property
def is_advisor(self):
    if self.advisor is None:
        return False
    return True


@property
def is_client(self):
    if self.client is None:
        return False
    return True

User.add_to_class("is_advisor", is_advisor)
User.add_to_class("is_client", is_client)