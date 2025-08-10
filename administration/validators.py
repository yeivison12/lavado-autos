from datetime import datetime
from django.utils.translation import gettext as _

def get_month_names():
    """Retorna un diccionario con los nombres de los meses en español."""
    return {
        1: _('Enero'), 2: _('Febrero'), 3: _('Marzo'), 4: _('Abril'),
        5: _('Mayo'), 6: _('Junio'), 7: _('Julio'), 8: _('Agosto'),
        9: _('Septiembre'), 10: _('Octubre'), 11: _('Noviembre'), 12: _('Diciembre')
    }

def validate_month(query):
    """Valida si la consulta es un nombre de mes en español."""
    month_names = get_month_names()
    for number, name in month_names.items():
        if query.lower() == name.lower():
            return number
    return None

def validate_day(query):
    """Valida si la consulta es un número de día válido."""
    try:
        day = int(query)
        if 1 <= day <= 31:
            return day
    except ValueError:
        pass
    return None

def validate_state(query):
    """Valida si la consulta es un estado ('disponible' o 'no disponible')."""
    if query.lower() in ['disponible', 'no disponible']:
        return query.lower() == 'disponible'
    return None

def validate_date_format(query):
    """Valida si la consulta es una fecha en formato 'día mes'."""
    try:
        date_query = datetime.strptime(query, '%d %B')
        return date_query.day, date_query.month
    except ValueError:
        return None