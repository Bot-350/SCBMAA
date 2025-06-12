from django.contrib import admin
from .models import Seccion, Capitulo, Partida, Subpartida

@admin.register(Seccion)
class SeccionAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'descripcion')

@admin.register(Capitulo)
class CapituloAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'descripcion', 'seccion')

@admin.register(Partida)
class PartidaAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'descripcion')

@admin.register(Subpartida)
class SubpartidaAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'descripcion', 'ga', 'ice_iehd', 'unidad_medida')