from django import template

register = template.Library()

@register.filter
def division(num, val):
    return num // val + 1