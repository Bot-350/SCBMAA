from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Subpartida, Partida, Capitulo, Seccion, Nota, RegistroCambio
import json


def obtener_cambios(instance, original=None):
    """Compara los datos actuales con los originales y retorna los cambios."""
    cambios = {}
    campos_a_rastrear = {
        'Subpartida': ['codigo', 'descripcion', 'ga', 'unidad_medida', 'tipo_de_doc', 
                       'entidad_que_emite', 'disposicion_legal', 'can_ace_36_47_ven',
                       'ace_22_chile', 'ace_22_prot', 'ace_66_mexico', 'es_titulo_intermedio', 'orden'],
        'Partida': ['codigo', 'descripcion', 'capitulo_id'],
        'Capitulo': ['codigo', 'nombre', 'descripcion', 'seccion_id'],
        'Seccion': ['nombre', 'descripcion'],
        'Nota': ['tipo', 'texto', 'es_lista', 'titulo_lista', 'seccion_id', 'capitulo_id'],
    }
    
    model_name = instance.__class__.__name__
    campos = campos_a_rastrear.get(model_name, [])
    
    for campo in campos:
        if hasattr(instance, campo):
            valor_actual = getattr(instance, campo, None)
            if original:
                valor_original = getattr(original, campo, None)
                if valor_actual != valor_original:
                    cambios[campo] = {
                        'anterior': str(valor_original),
                        'nuevo': str(valor_actual)
                    }
            else:
                cambios[campo] = str(valor_actual)
    
    return cambios


@receiver(post_save, sender=Subpartida)
@receiver(post_save, sender=Partida)
@receiver(post_save, sender=Capitulo)
@receiver(post_save, sender=Seccion)
@receiver(post_save, sender=Nota)
def registrar_cambio_creacion_actualizacion(sender, instance, created, **kwargs):
    """Registra cuando se crea o actualiza un objeto."""
    model_name = sender.__name__
    usuario = None
    
    # Intenta obtener el usuario de la solicitud actual
    try:
        from django.contrib.admin.models import LogEntry
        from django.contrib.contenttypes.models import ContentType
        
        # Obtener último cambio del admin para este objeto
        content_type = ContentType.objects.get_for_model(sender)
        ultimo_log = LogEntry.objects.filter(
            content_type=content_type,
            object_id=str(instance.pk)
        ).latest('action_time')
        usuario = ultimo_log.user.username if ultimo_log.user else 'Sistema'
    except:
        usuario = 'Sistema'
    
    if created:
        tipo_cambio = 'crear'
        cambios = obtener_cambios(instance)
        descripcion = f"Se creó un nuevo {model_name}"
    else:
        tipo_cambio = 'actualizar'
        cambios = obtener_cambios(instance)
        descripcion = f"Se actualizó {model_name}"
    
    RegistroCambio.objects.create(
        tipo_cambio=tipo_cambio,
        modelo=model_name,
        objeto_id=instance.pk,
        usuario=usuario,
        descripcion=descripcion,
        cambios_detalles=cambios
    )


@receiver(post_delete, sender=Subpartida)
@receiver(post_delete, sender=Partida)
@receiver(post_delete, sender=Capitulo)
@receiver(post_delete, sender=Seccion)
@receiver(post_delete, sender=Nota)
def registrar_cambio_eliminacion(sender, instance, **kwargs):
    """Registra cuando se elimina un objeto."""
    model_name = sender.__name__
    
    usuario = 'Sistema'
    try:
        from django.contrib.admin.models import LogEntry
        from django.contrib.contenttypes.models import ContentType
        
        content_type = ContentType.objects.get_for_model(sender)
        ultimo_log = LogEntry.objects.filter(
            content_type=content_type,
            object_id=str(instance.pk)
        ).latest('action_time')
        usuario = ultimo_log.user.username if ultimo_log.user else 'Sistema'
    except:
        pass
    
    RegistroCambio.objects.create(
        tipo_cambio='eliminar',
        modelo=model_name,
        objeto_id=instance.pk,
        usuario=usuario,
        descripcion=f"Se eliminó {model_name} con código/ID: {instance}",
        cambios_detalles={}
    )
