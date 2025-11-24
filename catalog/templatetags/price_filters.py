from django import template

register = template.Library()

@register.filter
def precio_format(value):
    """
    Formatea un precio con separador de miles (punto) y decimales (coma).
    Ejemplo: 177800.50 -> 177.800,50
    """
    try:
        # Convertir a float si es necesario
        num = float(value)
        
        # Separar parte entera y decimal
        entero = int(num)
        decimal = int(round((num - entero) * 100))
        
        # Formatear parte entera con separador de miles (punto)
        entero_str = f"{entero:,}".replace(",", ".")
        
        # Retornar con formato: entero.decimal,00
        return f"{entero_str},{decimal:02d}"
    except (ValueError, TypeError):
        return value
