from django.http import HttpResponse

def home_view(request):
    return HttpResponse("Bienvenido a la página principal de SCMAA")
