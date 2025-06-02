from django.contrib import admin
from .models import Seccion, Capitulo, Partida, Subpartida

@admin.register(Seccion)
class SeccionAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'descripcion')

@admin.register(Capitulo)
class CapituloAdmin(admin.ModelAdmin):
    list_display = ('id', 'codigo', 'nombre', 'seccion')

@admin.register(Partida)
class PartidaAdmin(admin.ModelAdmin):
    list_display = ('id', 'codigo', 'descripcion', 'capitulo', 'unidad_medida', 'documento_adicional', 'preferencias_arancelarias')

@admin.register(Subpartida)
class SubpartidaAdmin(admin.ModelAdmin):
    list_display = ('id', 'codigo', 'descripcion', 'partida', 'unidad_medida', 'documento_adicional', 'preferencias_arancelarias')
