from django import template

register = template.Library()

# Devuelve una cadena vacía para la tabla si el valor es None o vacío.

@register.filter
def blank_if_none(value):
    return value if value else ""