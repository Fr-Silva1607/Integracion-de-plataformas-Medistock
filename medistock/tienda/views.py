from django.shortcuts import render

# Create your views here.
from django.shortcuts import render

def home(request):
    return render(request, 'tienda/index.html')

from django.shortcuts import render

def home(request):
    return render(request, 'tienda/index.html')

def about(request):
    return render(request, 'tienda/about.html')

def contact(request):
    return render(request, 'tienda/contact.html')

def productos(request):
    return render(request, 'tienda/property.html')