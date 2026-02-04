from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """
    Obtém um item de um dicionário em um template.
    Uso: {{ dict|get_item:key }}
    """
    if dictionary and key in dictionary:
        return dictionary[key]
    return []
