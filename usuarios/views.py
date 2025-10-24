# views.py
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import Count
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie
from datetime import datetime, timedelta

from .models import SearchLog # Assuming SearchLog is in usuarios/models.py

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
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

@login_required
@require_POST
@csrf_protect
def log_search_term(request):
    term = request.POST.get('term', '').strip()
    if term:
        SearchLog.objects.create(user=request.user, term=term)
        return JsonResponse({'status': 'ok'})
    return JsonResponse({'status': 'error', 'message': 'No term provided'}, status=400)

@login_required
@require_POST
def save_search(request):
    """Vista para guardar una búsqueda via AJAX"""
    term = request.POST.get('term', '').strip()
    if term:
        SearchLog.objects.create(
            user=request.user,
            term=term
        )
        return JsonResponse({'status': 'ok'})
    return JsonResponse({'status': 'error', 'message': 'Término vacío'})

# Solo administradores pueden ver logs
@user_passes_test(lambda u: u.is_staff or u.is_superuser)
@login_required
def view_search_logs(request):
    """Vista para ver el historial de búsquedas"""
    try:
        # Obtener todos los usuarios que tienen logs
        user_ids = SearchLog.objects.values_list('user', flat=True).distinct()
        users_list = User.objects.filter(id__in=user_ids).order_by('username')

        selected_user_id = request.GET.get('user_id')
        selected_user_logs = None
        selected_user_instance = None

        # Filtro por fecha
        date_str = request.GET.get('date')
        selected_date = None
        logs = SearchLog.objects.select_related('user').order_by('-timestamp')

        if selected_user_id:
            try:
                selected_user_id = int(selected_user_id)
                selected_user_instance = User.objects.get(id=selected_user_id)
                logs = logs.filter(user_id=selected_user_id)
                selected_user_logs = logs  # Aplica ambos filtros si ambos están presentes
            except (ValueError, User.DoesNotExist):
                selected_user_id = None

        if date_str:
            try:
                selected_date = datetime.strptime(date_str, "%Y-%m-%d").date()
                logs = logs.filter(timestamp__date=selected_date)
                if selected_user_logs is not None:
                    selected_user_logs = selected_user_logs.filter(timestamp__date=selected_date)
            except ValueError:
                messages.error(request, "Fecha no válida. Formato esperado: AAAA-MM-DD.")

        context = {
            'logs': logs,
            'users_list': users_list,
            'selected_user_logs': selected_user_logs,
            'selected_user_instance': selected_user_instance,
            'selected_user_id': selected_user_id,
            'selected_date': date_str,
            'debug_info': {
                'total_logs': logs.count(),
                'request_user': request.user.username,
            }
        }
        return render(request, 'usuarios/search_logs.html', context)
    except Exception as e:
        import traceback
        context = {
            'error': str(e),
            'logs': [],
            'users_list': [],
            'selected_user_logs': None,
            'selected_user_instance': None,
            'selected_user_id': None,
            'debug_info': {
                'error_details': traceback.format_exc()
            }
        }
        return render(request, 'usuarios/search_logs.html', context)