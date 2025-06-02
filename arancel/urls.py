from django.urls import path
from .views import tabla_aranceles

app_name = 'arancel'

urlpatterns = [
    path('tabla/', tabla_aranceles, name='tabla_aranceles'),
]