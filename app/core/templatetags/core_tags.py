from django import template

register = template.Library()

@register.filter(name='formato_pesos')
def formato_pesos(value):
    if value is None or value == '':
        return "0"
    try:
        val_int = int(round(float(value)))
        return f"{val_int:,}".replace(",", ".")
    except (ValueError, TypeError):
        return value
