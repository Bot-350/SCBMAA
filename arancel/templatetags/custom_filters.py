from django import template

register = template.Library()

@register.filter
def blank_if_none(value):
    """Devuelve una cadena vacía si el valor es None o vacío."""
    return value if value else ""