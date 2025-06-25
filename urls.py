from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # ...existing code...
]

# Agrega las rutas estáticas directamente a urlpatterns
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)