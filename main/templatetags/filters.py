import datetime

from django.template import Library
from django.utils.safestring import mark_safe
from django.contrib.humanize.templatetags.humanize import intcomma

register = Library()


#example: {{ field|css:'active' }}
@register.filter(name='css')
def css(field, value):
    return field.as_widget(attrs={'class': value})


#example: {{ value|percantage100:2 }}
@register.filter
def percentage100(value, decimals=2):
    try:
        return ('%.' + str(decimals) + 'f') % (float(value) * 100) + '%'
    except ValueError:
        pass


#example: {{ value|percantage:2 }}
@register.filter
def percentage(value, decimals=2):
    try:
        return ('%.' + str(decimals) + 'f') % float(value) + '%'
    except ValueError:
        pass


#example: {{ value|currency:2:'$' }}
@register.filter
def currency(value, decimals=2, symbol='$'):
    try:
        value = round(float(value), 2)
        return "%s%s%s" % (symbol, intcomma(int(value)), ("%0.2f" % value)[-3:])
    except (ValueError, TypeError):
        return ''


#example: {{ birthday|age }}
@register.filter
def age(birthday, d=None):
    if d is None:
        d = datetime.date.today()
    return (d.year - birthday.year) - int((d.month, d.day) < (birthday.month, birthday.day))


@register.filter
def phone(value):
    if not value:
        return ''

    return value


# example: {{ request.resolver_match.view_name|menu_active:'url-name-a, url-name-b, url-name-c' }}
@register.filter
def menu_active(value, url_names=''):
    url_names = url_names.replace(' ', '').split(',')
    return 'active' if value in url_names else ''
