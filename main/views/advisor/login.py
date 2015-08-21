__author__ = 'cristian'

from ..utils.login import create_login
from main.models import Advisor

__all__ = ["advisor_login"]

advisor_login = create_login(Advisor, 'advisor')
