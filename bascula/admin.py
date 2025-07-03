from django.contrib import admin
from .models import Proveedor, Material, NotaDeEntrada, LineaDeNota # <-- AÑADIR NUEVOS MODELOS

# Registramos los modelos para que aparezcan en el panel de admin
admin.site.register(Proveedor)
admin.site.register(Material)
admin.site.register(NotaDeEntrada) # <-- AÑADIR
admin.site.register(LineaDeNota)   # <-- AÑADIR