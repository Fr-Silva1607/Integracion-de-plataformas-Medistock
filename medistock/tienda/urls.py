from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
]

from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('productos/', views.productos, name='productos'),
    path('login/', views.login, name='login'),
    path('registro/', views.registro, name='registro'),
    path('registro-empresa/', views.registroempresa, name='registroempresa'),
]