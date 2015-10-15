__author__ = 'cristian'
from django.forms import ModelForm
import inspect
from main.models import User

class T(ModelForm): pass




print(inspect.getclasstree([User]))