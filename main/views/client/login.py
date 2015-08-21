__author__ = 'cristian'

from ..utils.login import create_login
from main.models import Client

__all__ = ["client_login"]

client_login = create_login(Client, 'client')
