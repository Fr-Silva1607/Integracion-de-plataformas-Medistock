from django.urls import path
from . import views
from . import api

urlpatterns = [

    # WEB
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

    # WEBPAY
    path('webpay-iniciar/', views.webpay_iniciar, name='webpay_iniciar'),
    path('webpay-retorno/', views.webpay_retorno, name='webpay_retorno'),

  
    # API REST
    path('api/productos/', api.api_productos, name='api_productos'),
    path('api/productos/<int:producto_id>/', api.api_producto_detalle, name='api_producto_detalle'),
    path('api/productos/stock/', api.api_stock, name='api_stock'), 

    path('api/categorias/', api.api_categorias, name='api_categorias'),

    path('api/ordenes/', api.api_ordenes, name='api_ordenes'),
    path('api/crear-orden/', api.api_crear_orden, name='api_crear_orden'),

    path('api/dashboard/', api.api_dashboard, name='api_dashboard'),

    path('api/health/', api.api_health, name='api_health'),

    # Compatibilidad 
    path('api/calcular-total/', views.api_calcular_total, name='api_calcular_total'),
    path('api/status/', views.api_status, name='api_status'),

#RUTAS REGISTRADAS CHILEXPRESS
    path(
    'api/chilexpress/cotizar/',
    api.api_cotizar_envio,
    name='api_cotizar_envio'
),

path(
    'api/chilexpress/validar-direccion/',
    api.api_validar_direccion,
    name='api_validar_direccion'
),
]
