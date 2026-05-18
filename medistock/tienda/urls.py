from django.urls import path
from . import views
from . import api 

urlpatterns = [

    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('productos/', views.productos, name='productos'),
    path('producto/<int:producto_id>/', views.detalle_producto, name='detalle_producto'),
    path('login/', views.login, name='login'),
    path('registro/', views.registro, name='registro'),
    path('registro-empresa/', views.registroempresa, name='registroempresa'),
    path('carrito/', views.carrito, name='carrito'),
    path('pago/', views.pago, name='pago'),
    path('perfil/', views.perfil, name='perfil'),

    path('dashboard/', views.dashboard, name='dashboard'),
    path('api/ordenes/', api.api_ordenes),
    path('api/dashboard/', views.api_dashboard, name='api_dashboard'),

    path('webpay-iniciar/', views.webpay_iniciar, name='webpay_iniciar'),
    path('webpay-retorno/', views.webpay_retorno, name='webpay_retorno'),


    path('api/productos/', views.api_productos, name='api_productos'),
    path('api/calcular-total/', views.api_calcular_total, name='api_calcular_total'),
    path('api/status/', views.api_status, name='api_status'),
]

