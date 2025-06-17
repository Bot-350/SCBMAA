from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import Seccion, Partida, Subpartida # Nota: Django importa Nota automáticamente si es necesario, pero es bueno ser explícito
from usuarios.models import SearchLog

@login_required
def tabla_aranceles(request):
    """
    Vista principal que muestra la tabla de aranceles completa.
    
    Se ha modificado para usar prefetch_related de forma anidada, cargando
    las notas de cada sección y cada capítulo en consultas optimizadas.
    """
    secciones = Seccion.objects.prefetch_related(
        'notas',                          # ¡AÑADIDO! Carga todas las notas de esta sección.
        'capitulos__notas',               # ¡AÑADIDO! Carga todas las notas de cada capítulo.
        'capitulos__partidas__subpartidas'  # Mantiene la carga eficiente de partidas y subpartidas.
    ).all()
    
    context = {
        'secciones': secciones
    }
    return render(request, 'arancel/tabla_aranceles.html', context)

@login_required
def search_predictive(request):
    """
    Vista de búsqueda del lado del servidor. 
    NOTA: Esta vista no se usa actualmente si tu plantilla tiene un buscador
    basado en JavaScript que opera del lado del cliente.
    """
    query = request.GET.get('q', '').strip()

    if not query:
        return JsonResponse([], safe=False)

    if request.user.is_authenticated:
        SearchLog.objects.create(user=request.user, term=query)

    partida_query = Q(codigo__icontains=query) | Q(descripcion__icontains=query)
    subpartida_query = (Q(codigo__icontains=query) | Q(descripcion__icontains=query)) & ~Q(codigo__startswith='_H_')

    partidas = Partida.objects.filter(partida_query)
    subpartidas = Subpartida.objects.filter(subpartida_query)

    results = [
        {
            'type': 'partida',
            'codigo': p.codigo,
            'descripcion': p.descripcion,
        } for p in partidas
    ]
    results.extend([
        {
            'type': 'subpartida',
            'codigo': s.codigo,
            'descripcion': s.descripcion,
        } for s in subpartidas
    ])

    return JsonResponse(results[:20], safe=False)