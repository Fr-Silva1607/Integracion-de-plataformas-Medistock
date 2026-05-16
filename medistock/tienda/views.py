from django.shortcuts import render

# Create your views here.
from django.shortcuts import render

from django.conf import settings

def home(request):
    return render(request, 'tienda/index.html', {
        'SUPABASE_URL': settings.SUPABASE_URL,
        'SUPABASE_KEY': settings.SUPABASE_KEY,
    })

def login(request):
    return render(request, 'tienda/login.html', {
        'SUPABASE_URL': settings.SUPABASE_URL,
        'SUPABASE_KEY': settings.SUPABASE_KEY,
    })

def registro(request):
    return render(request, 'tienda/registro.html', {
        'SUPABASE_URL': settings.SUPABASE_URL,
        'SUPABASE_KEY': settings.SUPABASE_KEY,
    })

def registroempresa(request):
    return render(request, 'tienda/registro-empresa.html', {
        'SUPABASE_URL': settings.SUPABASE_URL,
        'SUPABASE_KEY': settings.SUPABASE_KEY,
    })

def about(request):
    return render(request, 'tienda/about.html')

def contact(request):
    return render(request, 'tienda/contact.html')

def productos(request):
    return render(request, 'tienda/property.html')

