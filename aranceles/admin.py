from django.contrib import admin
from .models import Seccion, Capitulo, Partida, Subpartida, Nota, ItemNota

@admin.register(Seccion)
class SeccionAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'descripcion')
    ordering = ('id',) 

class ItemNotaInline(admin.TabularInline):
    model = ItemNota
    extra = 1 

@admin.register(Nota)
class NotaAdmin(admin.ModelAdmin):
    list_display = ('id', 'tipo', 'texto_corto', 'seccion', 'capitulo')
    list_filter = ('tipo', 'seccion', 'capitulo')
    inlines = [ItemNotaInline] 

    def texto_corto(self, obj):
        if obj.es_lista:
            return obj.titulo_lista
        return (obj.texto[:75] + '...') if len(obj.texto) > 75 else obj.texto
    texto_corto.short_description = 'Texto o Título'

@admin.register(Capitulo)
class CapituloAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'seccion')
    list_filter = ('seccion',)
    ordering = ('codigo',)

@admin.register(Partida)
class PartidaAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'descripcion', 'capitulo')
    list_filter = ('capitulo__seccion', 'capitulo')
    search_fields = ('codigo', 'descripcion')
    ordering = ('codigo',)

@admin.register(Subpartida)
class SubpartidaAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'descripcion', 'ga', 'unidad_medida', 'partida')
    list_filter = ('partida__capitulo__seccion', 'partida__capitulo')
    search_fields = ('codigo', 'descripcion')
    ordering = ('codigo',)

