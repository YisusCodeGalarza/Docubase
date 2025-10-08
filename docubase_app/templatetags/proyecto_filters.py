from django import template
from django.utils.html import strip_tags
from html import unescape
import re

register = template.Library()

@register.filter
def clean_description(value, chars=120):
    """
    Limpia la descripción: remueve HTML tags, decodifica caracteres especiales
    y trunca el texto.
    """
    if not value:
        return ""
    
    # 1. Remover etiquetas HTML
    clean_text = strip_tags(value)
    
    # 2. Decodificar caracteres HTML (como &aacute; -> á)
    clean_text = unescape(clean_text)
    
    # 3. Remover espacios extras y saltos de línea
    clean_text = re.sub(r'\s+', ' ', clean_text).strip()
    
    # 4. Truncar a cierto número de caracteres
    if len(clean_text) > chars:
        return clean_text[:chars] + '...'
    
    return clean_text