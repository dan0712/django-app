import re
import ujson
from django import forms
from django.conf import settings
from django.core.validators import RegexValidator
from django.db import models
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _

color_re = re.compile('^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$')
validate_color = RegexValidator(color_re, _('Enter a valid color.'), 'invalid')


class ColorWidget(forms.Widget):
    class Media:
        js = [settings.STATIC_URL + 'colorfield/jscolor/jscolor.js']

    def render(self, name, value, attrs=None):
        return render_to_string('colorfield/color.html', locals())


class ColorField(models.CharField):
    default_validators = [validate_color]

    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 10
        super(ColorField, self).__init__(*args, **kwargs)

    def formfield(self, **kwargs):
        kwargs['widget'] = ColorWidget
        return super(ColorField, self).formfield(**kwargs)


class TaxFileNumberValidator(object):
    def __call__(self, value):

        if len(value) != 9:
            return False, 'Invalid TFN, check the digits.'

        weights = [1, 4, 3, 7, 5, 8, 6, 9, 10]
        _sum = 0

        try:
            for i in range(9):
                _sum += int(value[i]) * weights[i]
        except ValueError:
            return False, 'Invalid TFN, check the digits.'

        remainder = _sum % 11

        if remainder != 0:
            return False, 'Invalid TFN, check the digits.'

        return True, ""


class MedicareNumberValidator(object):
    def __call__(self, value):

        if len(value) != 11:
            return False, 'Invalid Medicare number.'

        weights = [1, 3, 7, 9, 1, 3, 7, 9]
        _sum = 0

        try:
            check_digit = int(value[8])
            for i in range(8):
                _sum += int(value[i]) * weights[i]
        except ValueError:
            return False, 'Invalid Medicare number.'

        remainder = _sum % 10

        if remainder != check_digit:
            return False, 'Invalid Medicare number.'

        return True, ""
