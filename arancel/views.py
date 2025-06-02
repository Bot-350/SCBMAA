from django.shortcuts import render
from .models import Seccion

def tabla_aranceles(request):
    secciones = Seccion.objects.prefetch_related('capitulos__partidas__subpartidas')
    return render(request, 'arancel/tabla_aranceles.html', {'secciones': secciones})