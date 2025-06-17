# views.py
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import Count

from .models import SearchLog # Assuming SearchLog is in usuarios/models.py

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'Has iniciado sesión correctamente.')
            # Redirige a la página que el usuario intentaba acceder o a home
            next_url = request.GET.get('next', 'home')
            return redirect(next_url)
        else:
            messages.error(request, 'Usuario o contraseña incorrectos.')
    
    return render(request, 'usuarios/login.html')

def logout_view(request):
    logout(request)
    return redirect('home')

@login_required
def profile_view(request):
    """Vista para mostrar el perfil del usuario"""
    user = request.user
    context = {
        'user': user,
        'username': user.username,
        'email': user.email,
    }
    return render(request, 'usuarios/perfil.html', context)

@login_required
def change_password(request):
    """Vista para cambiar la contraseña"""
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            # Mantener la sesión activa después del cambio de contraseña
            update_session_auth_hash(request, user)
            messages.success(request, 'Tu contraseña ha sido cambiada exitosamente.')
            return redirect('usuarios:perfil') # Corrected redirect
        else:
            messages.error(request, 'Por favor corrige los errores.')
    else:
        form = PasswordChangeForm(request.user)
    
    return render(request, 'usuarios/re_contraseña.html', {'form': form})

@login_required
def search_logs_dashboard_view(request):
    # Daily Logs
    today = timezone.now().date()
    daily_logs = SearchLog.objects.filter(timestamp__date=today).order_by('-timestamp')

    # User List for selection
    users_list = User.objects.all().order_by('username')

    # User-Specific Logs
    selected_user_id = request.GET.get('user_id')
    selected_user_logs = None
    selected_user_instance = None

    if selected_user_id:
        try:
            # Ensure selected_user_id is a valid integer
            selected_user_id = int(selected_user_id)
            selected_user_instance = User.objects.get(id=selected_user_id)
            selected_user_logs = SearchLog.objects.filter(user_id=selected_user_id).order_by('-timestamp')
        except (ValueError, User.DoesNotExist):
            messages.error(request, "Usuario seleccionado no válido.")
            selected_user_id = None # Reset if invalid

    # Most Searched Terms
    most_searched_terms = SearchLog.objects.values('term').annotate(count=Count('term')).order_by('-count')[:10]

    context = {
        'daily_logs': daily_logs,
        'users_list': users_list,
        'selected_user_logs': selected_user_logs,
        'selected_user_instance': selected_user_instance, # Pass the user instance for display
        'selected_user_id': selected_user_id, # Pass the ID for template logic (e.g., pre-selecting in dropdown)
        'most_searched_terms': most_searched_terms,
        'page_title': 'Dashboard de Búsquedas' # Added for clarity in template
    }
    return render(request, 'usuarios/search_logs_page.html', context)