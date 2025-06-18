from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class SearchLog(models.Model):
    """
    Modelo para registrar las búsquedas realizadas por los usuarios
    """
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name='search_logs',
        verbose_name='Usuario'
    )
    term = models.CharField(
        max_length=255,
        verbose_name='Término buscado'
    )
    timestamp = models.DateTimeField(
        default=timezone.now,
        verbose_name='Fecha y hora'
    )

    class Meta:
        verbose_name = 'Registro de búsqueda'
        verbose_name_plural = 'Registros de búsquedas'
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.user.username} buscó '{self.term}' el {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"

