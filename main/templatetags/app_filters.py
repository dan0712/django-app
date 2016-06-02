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
    if not value:
        return '' 
    return '%02d/%02d/%d' % (value.day, value.month, value.year)


@register.filter
def b_datetime(value):
    return value.strftime("%d/%m/%Y %H:%M")


@register.filter
def c_datetime(value):
    if value:
        return value.strftime('%Y%m%d%H%M%S')
    return ""


@register.filter
def bs_big_number(value):
    if isinstance(value, str):
        return value
    new_v = "{:,}".format(float("{0:.2f}".format(value)))
    if new_v == "0.0":
        return "0.00"
    try:
        d, f = new_v.split(".")
        if len(f) == 1:
            new_v += "0"
    except:
        pass
    return new_v


@register.filter
def phone_format(value):
    if not value:
        return ""
    if value[:4] == "1888" or value[:4] == "1800":
        return value[:4] + "-" + value[4:8] + "-" + value[8:10]
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


@register.filter
def add_class_id(field, css_id):
    css, _id = css_id.split(", ")
    return field.as_widget(attrs={"class": css, "id": _id})
