from django.core.management.base import BaseCommand
from aranceles.models import Subpartida


def natural_key(codigo):
    if not codigo:
        return ()
    codigo = str(codigo)
    if codigo.startswith('_H_'):
        return (float('inf'), codigo)
    parts = [p for p in codigo.replace('-', '.').split('.') if p != '']
    key = []
    for p in parts:
        try:
            key.append(int(p))
        except ValueError:
            key.append(p.lower())
    return tuple(key)


class Command(BaseCommand):
    help = 'Recalcula el campo orden de Subpartida para cada partida usando orden natural por codigo'

    def handle(self, *args, **options):
        partidas = set(Subpartida.objects.values_list('partida_id', flat=True))
        total_changed = 0
        for pid in partidas:
            sps = list(Subpartida.objects.filter(partida_id=pid))
            if not sps:
                continue
            sps_sorted = sorted(sps, key=lambda s: natural_key(s.codigo))
            changed = []
            for i, sp in enumerate(sps_sorted, start=1):
                if sp.orden != i:
                    sp.orden = i
                    changed.append(sp)
            if changed:
                Subpartida.objects.bulk_update(changed, ['orden'])
                total_changed += len(changed)
        self.stdout.write(self.style.SUCCESS(f'Recalculado orden para {len(partidas)} partidas. Registros actualizados: {total_changed}'))
