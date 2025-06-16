from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = 'usuarios'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('perfil/', views.profile_view, name='profile'),
    path('perfil/cambiar-contraseña/', views.change_password, name='change_password'),

    # New URL for the search logs dashboard
    path('logs/', views.search_logs_dashboard_view, name='search_logs_dashboard'),
]