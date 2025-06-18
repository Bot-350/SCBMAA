from django.urls import path
from . import views

app_name = 'usuarios'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('perfil/', views.profile_view, name='perfil'),
    path('perfil/cambiar-contraseña/', views.change_password, name='change_password'),
    path('logs/', views.view_search_logs, name='search_logs'),
    path('save-search/', views.save_search, name='save_search'),
]