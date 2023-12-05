# myapp/templatetags/widget_tags.py

from django import template

register = template.Library()

@register.filter(name='widget_class')
def widget_class(field):
    return field.field.widget.__class__.__name__
