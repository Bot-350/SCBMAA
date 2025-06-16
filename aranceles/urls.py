from django.urls import path
from .views import tabla_aranceles, search_predictive

app_name = 'aranceles'

urlpatterns = [
    path('tabla/', tabla_aranceles, name='tabla_aranceles'),
    path('search/', search_predictive, name='search_predictive'), # Added path for search_predictive
]