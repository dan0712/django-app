__author__ = 'cristian'

from django import template
register = template.Library()


@register.filter
def add_class(value, index):
    """
    Add a tabindex attribute to the widget for a bound field.
    """

    if 'class' not in value.field.widget.attrs:
        value.field.widget.attrs['class'] = index
    return value


@register.filter
def b_date(value):
    return "%02d/%02d/%d" % (value.day, value.month, value.year)


@register.filter
def b_datetime(value):
    return value.strftime("%d/%m/%Y %H:%M")


@register.filter
def c_datetime(value):
    return value.strftime('%Y%m%d%H%M%S')


@register.filter
def bs_big_number(value):
    if isinstance(value, str):
        return value
    new_v = "{:,}".format(float("{0:.2f}".format(value)))
    if new_v == "0.0":
        return "0.00"
    return new_v


@register.filter
def phone_format(value):
    if value[:2] == "04":
        return value[:4] + "-" + value[4:7] + "-" + value[7:10]
    return value[:2] + "-" + value[2:6] + "-" + value[6:10]


@register.filter
def json_none(value):
    if value is True:
        return "true"
    if value is False:
        return "false"
    if value is None:
        return "null"
    return value
