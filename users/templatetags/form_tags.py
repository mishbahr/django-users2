from django import forms
from django import template

register = template.Library()

from users.fields import HoneyPotField


@register.filter
def is_checkbox(field):
    return isinstance(field.field.widget, forms.CheckboxInput)


@register.filter
def input_class(field):
    """
    Returns widgets class name in lowercase
    """
    return field.field.widget.__class__.__name__.lower()


@register.filter
def is_honeypot(field):
    return isinstance(field.field, HoneyPotField)
