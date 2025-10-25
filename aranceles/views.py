from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import Seccion, Partida, Subpartida
from usuarios.models import SearchLog

@login_required
def tabla_aranceles(request):

    secciones = Seccion.objects.prefetch_related(
        'notas',
        'capitulos__notas',
        'capitulos__partidas__subpartidas'
    ).all()
    
    context = {
        'secciones': secciones
    }
    return render(request, 'arancel/tabla_aranceles.html', context)

@login_required
def search_predictive(request):
   
   
    query = request.GET.get('q', '').strip()

    
    if not query:
        return JsonResponse([], safe=False)


    if request.user.is_authenticated:
        SearchLog.objects.create(user=request.user, term=query)

   
    partida_query = Q(codigo__icontains=query) | Q(descripcion__icontains=query)
    subpartida_query = (Q(codigo__icontains=query) | Q(descripcion__icontains=query)) & ~Q(codigo__startswith='_H_')

  
    partidas = Partida.objects.filter(partida_query)[:5]
    subpartidas = Subpartida.objects.filter(subpartida_query)[:5]

   
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

    return JsonResponse(results[:5], safe=False)