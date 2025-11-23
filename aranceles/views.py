from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import Seccion, Partida, Subpartida, RegistroCambio
from usuarios.models import SearchLog
from django.db.models import Avg, Max, Min, Count
from .models import Capitulo
from datetime import timedelta
from django.utils import timezone

@login_required
def tabla_aranceles(request):
    """
    Vista principal que muestra la tabla de aranceles completa.
    
    Se ha modificado para usar prefetch_related de forma anidada, cargando
    las notas de cada sección y cada capítulo en consultas optimizadas.
    
    Enriquece cada subpartida con su fecha de última modificación desde RegistroCambio.
    """
    # Calcular fecha hace 30 días
    fecha_hace_30_dias = timezone.now() - timedelta(days=30)
    
    secciones = Seccion.objects.prefetch_related(
        'notas',
        'capitulos__notas',
        'capitulos__partidas__subpartidas'
    ).all()
    
    # Enriquecer subpartidas con fecha de última modificación desde RegistroCambio
    for seccion in secciones:
        for capitulo in seccion.capitulos.all():
            for partida in capitulo.partidas.all():
                for subpartida in partida.subpartidas.all():
                    # Obtener el último registro de cambio para esta subpartida
                    ultimo_cambio = RegistroCambio.objects.filter(
                        modelo='Subpartida',
                        objeto_id=subpartida.id
                    ).order_by('-fecha').first()
                    
                    # Asignar dinámicamente como atributo (no es campo de BD)
                    subpartida.fecha_ultima_modificacion = ultimo_cambio.fecha if ultimo_cambio else None
    
    context = {
        'secciones': secciones,
        'fecha_hace_30_dias': fecha_hace_30_dias
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


@login_required
def estadisticas_gravamenes(request):
    """
    Calcula estadísticas básicas (promedio, máximo, mínimo) del campo `ga`
    por capítulo y las pasa a la plantilla.
    """
    estadisticas = []

    # Traer capítulos con sus partidas y subpartidas para reducir consultas
    capitulos = Capitulo.objects.prefetch_related('partidas__subpartidas').all()

    for cap in capitulos:
        # Obtener todas las subpartidas relacionadas y filtrar ga no nulo
        subparts = [s for p in cap.partidas.all() for s in p.subpartidas.all() if s.ga is not None]
        cantidad = len(subparts)
        if cantidad == 0:
            estadisticas.append({
                'capitulo': cap,
                'promedio': None,
                'maximo': None,
                'minimo': None,
                'cantidad': 0
            })
            continue

        # Convertir a floats para cálculos
        ga_vals = [float(s.ga) for s in subparts]
        promedio = sum(ga_vals) / len(ga_vals)
        maximo = max(ga_vals)
        minimo = min(ga_vals)

        estadisticas.append({
            'capitulo': cap,
            'promedio': promedio,
            'maximo': maximo,
            'minimo': minimo,
            'cantidad': cantidad
        })

    context = {
        'estadisticas': estadisticas
    }
    return render(request, 'arancel/estadisticas.html', context)