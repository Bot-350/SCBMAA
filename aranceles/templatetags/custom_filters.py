from django import template

register = template.Library()

# Devuelve una cadena vacia para la tabla si el valor es None o vacío.

@register.filter
def blank_if_none(value):
    return value if value else ""


@register.filter
def remove_leading_zeros(value):
    """Remueve los ceros iniciales de una cadena, ej: '01' -> '1'"""
    if value is None:
        return ''
    try:
        s = str(value)
        return s.lstrip('0') or '0'
    except Exception:
        return value


@register.filter
def format_search_term(value):
    """Formatea un término de búsqueda para mostrar tipo 'Capítulo N' cuando aplica.

    Si el valor es un número de uno o dos dígitos (por ejemplo '1' o '01'), devuelve
    'Capítulo N' sin ceros a la izquierda. En otro caso devuelve el valor original.
    Extrae el código antes del ' - ' o ' -' si existe (ej. '01 - Descripción' -> '01').
    """
    if value is None:
        return ''
    try:
        s = str(value).strip()
        # Extraer código si hay ' - ' o ' -' (formato guardado: "código - descripción" o "código -")
        if ' -' in s:
            s = s.split(' -')[0].strip()
        import re
        # Remover cualquier texto tipo 'CAPÍTULO', 'CAP', etc. al inicio
        s = re.sub(r'^[a-zA-Z\s]+', '', s).strip()
        # Capítulo: 1-2 dígitos
        if s.isdigit() and len(s) <= 2:
            n = s.lstrip('0') or '0'
            return f'Capítulo {n}'
        # Partida: formato DD.DD (dos dígitos punto dos dígitos)
        if re.match(r'^\d{2}\.\d{2}$', s):
            return f'Partida {s}'
        # Subpartida: más largo (ej. DD.DD.DDD o cadenas de dígitos > 4)
        if re.match(r'^[\d\.]+$', s) and len(s.replace('.', '')) > 4:
            return f'Subpartida {s}'
    except Exception:
        pass
    return value


@register.filter
def search_term_class(value):
    """Clasifica el término de búsqueda en una clase CSS simple:

    - 'capitulo' para números de 1-2 dígitos (ej. '1', '01')
    - 'partida' para números de 4 dígitos (ej. '0101')
    - 'subpartida' para códigos más largos
    - 'texto' por defecto
    
    Extrae el código antes del ' - ' o ' -' si existe (ej. '01 - Descripción' o '01 -' -> '01').
    Valida si comienza con dígitos.
    """
    if value is None:
        return 'texto'
    try:
        s = str(value).strip()
        # Extraer código si hay ' - ' o ' -' (formato guardado: "código - descripción" o "código -")
        if ' -' in s:
            s = s.split(' -')[0].strip()
        import re
        
        # Remover cualquier texto tipo 'CAPÍTULO', 'CAP', etc. al inicio
        s = re.sub(r'^[a-zA-Z\s]+', '', s).strip()
        
        # capítulo: 1-2 dígitos (acepta '1' y también '01')
        if s.isdigit() and len(s) <= 2:
            return 'capitulo'
        # partida: formato DD.DD
        if re.match(r'^\d{2}\.\d{2}$', s):
            return 'partida'
        # subpartida: cadena de dígitos/puntos con más de 4 dígitos totales
        if re.match(r'^[\d\.]+$', s) and len(s.replace('.', '')) > 4:
            return 'subpartida'
    except Exception:
        pass
    return 'texto'


@register.filter
def search_term_style(value):
    """Devuelve una cadena de estilo inline para el término de búsqueda.

    Se usa para forzar color y bordes directamente en el elemento HTML, evitando
    que frameworks como Bootstrap sobrescriban las reglas.
    """
    try:
        cls = search_term_class(value)
        if cls == 'capitulo':
            return 'background:#fdecea;color:#b91c1c;border:none;box-shadow:none;padding:4px 10px;border-radius:12px;'
        if cls == 'partida':
            return 'background:#e6fbef;color:#138000;border:none;box-shadow:none;padding:4px 10px;border-radius:12px;'
        if cls == 'subpartida':
            return 'background:#eef6ff;color:#0b5cff;border:none;box-shadow:none;padding:4px 10px;border-radius:12px;'
    except Exception:
        pass
    # texto u otros
    return 'background:#f1f3f5;color:#495057;border:none;box-shadow:none;padding:4px 10px;border-radius:12px;'