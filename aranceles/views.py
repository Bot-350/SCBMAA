from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Seccion, Partida, Subpartida
from usuarios.models import SearchLog # Import SearchLog

@login_required
def tabla_aranceles(request):
    secciones = Seccion.objects.prefetch_related('capitulos__partidas__subpartidas')
    return render(request, 'arancel/tabla_aranceles.html', {'secciones': secciones})

@login_required
def search_predictive(request):
    query = request.GET.get('q', '').strip()  # Obtén el término de búsqueda

    # Log the search term if the query is not empty
    if query and request.user.is_authenticated: # Ensure user is authenticated
        SearchLog.objects.create(user=request.user, term=query)

    if not query:
        return JsonResponse([], safe=False)

    # Buscar por código exacto en partidas y subpartidas
    partidas = Partida.objects.filter(codigo__icontains=query)
    subpartidas = Subpartida.objects.filter(codigo__icontains=query)

    # Buscar por palabras en la descripción
    partidas_descripcion = Partida.objects.filter(descripcion__icontains=query)
    subpartidas_descripcion = Subpartida.objects.filter(descripcion__icontains=query)

    # Combinar resultados
    results = []
    for partida in partidas.union(partidas_descripcion):
        results.append({
            'type': 'partida',
            'codigo': partida.codigo,
            'descripcion': partida.descripcion,
        })

    for subpartida in subpartidas.union(subpartidas_descripcion):
        results.append({
            'type': 'subpartida',
            'codigo': subpartida.codigo,
            'descripcion': subpartida.descripcion,
        })

    return JsonResponse(results, safe=False)