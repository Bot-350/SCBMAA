# views.py
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import PasswordChangeForm, UserCreationForm
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import Count
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie
from django import forms
from django.core.exceptions import ValidationError as DjangoValidationError
from django.contrib.auth import password_validation
from datetime import datetime, timedelta

from .models import SearchLog # Assuming SearchLog is in usuarios/models.py


class CustomUserCreationForm(UserCreationForm):
    """Formulario personalizado para crear usuarios con campos adicionales"""
    email = forms.EmailField(required=False, help_text='Opcional. Email válido si se proporciona.')
    first_name = forms.CharField(max_length=30, required=False, help_text='Opcional.')
    last_name = forms.CharField(max_length=30, required=False, help_text='Opcional.')
    
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')
        labels = {
            'username': 'Nombre de usuario',
            'email': 'Correo electrónico',
            'first_name': 'Nombre',
            'last_name': 'Apellido',
            'password1': 'Contraseña',
            'password2': 'Confirmar contraseña',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Etiquetas y textos de ayuda en español
        self.fields['username'].label = 'Nombre de usuario'
        self.fields['username'].help_text = 'Requerido. 150 caracteres o menos. Letras, dígitos y @/./+/-/_ solo.'

        self.fields['email'].label = 'Correo electrónico'
        self.fields['email'].help_text = 'Opcional. Email válido si se proporciona.'

        self.fields['first_name'].label = 'Nombre'
        self.fields['first_name'].help_text = 'Opcional.'

        self.fields['last_name'].label = 'Apellido'
        self.fields['last_name'].help_text = 'Opcional.'

        # Campos de contraseña: etiquetas y ayuda claras en español
        if 'password1' in self.fields:
            self.fields['password1'].label = 'Contraseña'
            # Help text detallado en español (coincide con validadores comunes)
            self.fields['password1'].help_text = (
                '<ul style="margin:6px 0 0 18px;padding:0;line-height:1.4;">'
                '<li>Tu contraseña no puede ser demasiado similar a tu información personal.</li>'
                '<li>La contraseña debe contener al menos 8 caracteres.</li>'
                '<li>La contraseña no puede ser una contraseña de uso común.</li>'
                '<li>La contraseña no puede ser totalmente numérica.</li>'
                '</ul>'
            )
        if 'password2' in self.fields:
            self.fields['password2'].label = 'Confirmar contraseña'
            self.fields['password2'].help_text = 'Introduce la misma contraseña para verificación.'

        # Mensajes de error en español (algunos ya vienen traducidos si usas i18n)
        self.fields['username'].error_messages.update({
            'required': 'El nombre de usuario es obligatorio.',
            'unique': 'Ya existe un usuario con ese nombre.'
        })
        self.fields['email'].error_messages.update({
            'invalid': 'Introduce una dirección de correo electrónico válida.'
        })

    def clean_password1(self):
        """Validar la contraseña y traducir mensajes de validación al español."""
        password = self.cleaned_data.get('password1')
        if not password:
            return password
        try:
            password_validation.validate_password(password, self.instance)
        except DjangoValidationError as e:
            translated = []
            for msg in e.messages:
                lower = msg.lower()
                if 'similar' in lower or 'similar to' in lower:
                    translated.append('Tu contraseña no puede ser demasiado similar a tu información personal.')
                elif 'at least' in lower or '8 characters' in lower or '8 caracteres' in lower:
                    translated.append('La contraseña debe contener al menos 8 caracteres.')
                elif 'commonly used' in lower or 'common' in lower:
                    translated.append('La contraseña no puede ser una contraseña de uso común.')
                elif 'entirely numeric' in lower or 'only numbers' in lower or 'numér' in lower:
                    translated.append('La contraseña no puede ser totalmente numérica.')
                else:
                    translated.append(msg)
            raise forms.ValidationError(translated)
        return password


class CustomPasswordChangeForm(PasswordChangeForm):
    """Form de cambio de contraseña que traduce los mensajes de validación."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'new_password1' in self.fields:
            self.fields['new_password1'].label = 'Nueva contraseña'
            self.fields['new_password1'].help_text = (
                '<ul style="margin:6px 0 0 18px;padding:0;line-height:1.4;">'
                '<li>Tu contraseña no puede ser demasiado similar a tu información personal.</li>'
                '<li>La contraseña debe contener al menos 8 caracteres.</li>'
                '<li>La contraseña no puede ser una contraseña de uso común.</li>'
                '<li>La contraseña no puede ser totalmente numérica.</li>'
                '</ul>'
            )

    def clean_new_password1(self):
        password = self.cleaned_data.get('new_password1')
        if not password:
            return password
        try:
            password_validation.validate_password(password, self.user)
        except DjangoValidationError as e:
            translated = []
            for msg in e.messages:
                lower = msg.lower()
                if 'similar' in lower or 'similar to' in lower:
                    translated.append('Tu contraseña no puede ser demasiado similar a tu información personal.')
                elif 'at least' in lower or '8 characters' in lower or '8 caracteres' in lower:
                    translated.append('La contraseña debe contener al menos 8 caracteres.')
                elif 'commonly used' in lower or 'common' in lower:
                    translated.append('La contraseña no puede ser una contraseña de uso común.')
                elif 'entirely numeric' in lower or 'only numbers' in lower or 'numér' in lower:
                    translated.append('La contraseña no puede ser totalmente numérica.')
                else:
                    translated.append(msg)
            raise forms.ValidationError(translated)
        return password
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        # Si no se proporcionó email, no validar unicidad (es opcional)
        if email:
            if User.objects.filter(email=email).exists():
                raise forms.ValidationError('Este correo electrónico ya está en uso.')
        return email
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data.get('email', '')
        user.first_name = self.cleaned_data.get('first_name', '')
        user.last_name = self.cleaned_data.get('last_name', '')
        if commit:
            user.save()
        return user

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
        form = CustomPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            # Mantener la sesión activa después del cambio de contraseña
            update_session_auth_hash(request, user)
            messages.success(request, 'Tu contraseña ha sido cambiada exitosamente.')
            # No redirigimos: mantenemos al usuario en la misma página con el formulario vaciado
            form = CustomPasswordChangeForm(request.user)
        else:
            messages.error(request, 'Por favor corrige los errores.')
    else:
        form = CustomPasswordChangeForm(request.user)
    
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

        if selected_user_id:
            try:
                selected_user_id = int(selected_user_id)
                selected_user_instance = User.objects.get(id=selected_user_id)
                selected_user_logs = SearchLog.objects.filter(user_id=selected_user_id).order_by('-timestamp')
            except (ValueError, User.DoesNotExist):
                selected_user_id = None

        logs = SearchLog.objects.select_related('user').order_by('-timestamp')

        context = {
            'logs': logs,
            'users_list': users_list,
            'selected_user_logs': selected_user_logs,
            'selected_user_instance': selected_user_instance,
            'selected_user_id': selected_user_id,
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


# Solo administradores pueden crear usuarios
@user_passes_test(lambda u: u.is_staff or u.is_superuser)
@login_required
def create_user(request):
    """Vista para crear nuevos usuarios"""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            username_created = form.cleaned_data.get('username')
            form.save()
            messages.success(request, f'Usuario {username_created} creado exitosamente.')
            # No redirigir: dejar el formulario vacío para que el admin pueda seguir añadiendo usuarios
            form = CustomUserCreationForm()
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    # Mostrar errores con etiquetas en español si es posible
                    messages.error(request, f'{field}: {error}')
    else:
        form = CustomUserCreationForm()

    return render(request, 'usuarios/crear_usuario.html', {'form': form})