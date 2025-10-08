from django.contrib import admin
from .models import Etiqueta, Proyecto, Pagina, Archivo, Comentario

# Registra tus modelos aquí.
admin.site.register(Etiqueta)
admin.site.register(Proyecto)
admin.site.register(Pagina)
admin.site.register(Archivo)
admin.site.register(Comentario)
