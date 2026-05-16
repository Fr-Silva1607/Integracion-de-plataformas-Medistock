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
    return render(request, 'tienda/about.html', {
        'SUPABASE_URL': settings.SUPABASE_URL,
        'SUPABASE_KEY': settings.SUPABASE_KEY,
    })


def contact(request):
    return render(request, 'tienda/contact.html', {
        'SUPABASE_URL': settings.SUPABASE_URL,
        'SUPABASE_KEY': settings.SUPABASE_KEY,
    })


def productos(request):
    return render(request, 'tienda/productos.html', {
        'SUPABASE_URL': settings.SUPABASE_URL,
        'SUPABASE_KEY': settings.SUPABASE_KEY,
    })


def detalle_producto(request, producto_id):
    return render(request, 'tienda/detalle-producto.html', {
        'SUPABASE_URL': settings.SUPABASE_URL,
        'SUPABASE_KEY': settings.SUPABASE_KEY,
        'producto_id': producto_id,
    })


def carrito(request):
    return render(request, 'tienda/Carrito.html', {
        'SUPABASE_URL': settings.SUPABASE_URL,
        'SUPABASE_KEY': settings.SUPABASE_KEY,
    })


def pago(request):
    orden_id = request.GET.get('orden')
    return render(request, 'tienda/pago.html', {
        'SUPABASE_URL': settings.SUPABASE_URL,
        'SUPABASE_KEY': settings.SUPABASE_KEY,
        'orden_id': orden_id,
    })


def perfil(request):
    return render(request, 'tienda/perfil.html', {
        'SUPABASE_URL': settings.SUPABASE_URL,
        'SUPABASE_KEY': settings.SUPABASE_KEY,
    })

import random
from django.shortcuts import render, redirect
from django.conf import settings
from transbank.webpay.webpay_plus.transaction import Transaction
from transbank.common.options import WebpayOptions
from transbank.common.integration_type import IntegrationType

# 1. Configurar la conexión con las credenciales de prueba
def get_webpay_options():
    # En producción reemplazarías estos strings por variables de tu settings.py (.env)
    commerce_code = "597055555532"
    api_key = "579B532A7440BB0C9079DED94D31EA1615B119517446553A547425419C83FF1B"
    
    # Indicamos que estamos en el ambiente de TEST (Integración)
    return WebpayOptions(commerce_code, api_key, IntegrationType.TEST)


# VISTA 1: Iniciar el pago y redirigir al usuario a Transbank
def webpay_iniciar(request):
    # Datos de la compra (puedes sacarlos de tu sesión, carrito o BD)
    buy_order = f"O-{random.randint(10000, 99999)}" # Orden de compra única
    session_id = request.session.session_key or "session_anonima"
    amount = 15500 # El total en CLP (debe ser entero)
    
    # URL de retorno: adonde Transbank enviará al usuario con el token de pago
    return_url = request.build_absolute_uri('/tienda/webpay-retorno/')

    try:
        # Inicializar la transacción con nuestras opciones configuradas
        tx = Transaction(get_webpay_options())
        response = tx.create(buy_order, session_id, amount, return_url)
        
        # Transbank nos devuelve una URL y un Token único
        # Debemos renderizar un formulario automático que viaje hacia allá
        return render(request, 'tienda/webpay_redirect.html', {
            'url': response['url'],
            'token': response['token']
        })
        
    except Exception as e:
        print(f"Error al crear la transacción: {e}")
        return render(request, 'tienda/error.html', {'mensaje': 'No se pudo iniciar el pago.'})


# VISTA 2: El retorno (Donde confirmamos si el pago fue exitoso)
def webpay_retorno(request):
    # Webpay envía el token por método GET o POST dependiendo del flujo
    token = request.GET.get('token_ws') or request.POST.get('token_ws')
    
    if not token:
        # Si no hay token, es probable que el usuario haya cancelado en la pantalla de Transbank
        return render(request, 'tienda/error.html', {'mensaje': 'Pago cancelado por el usuario.'})

    try:
        tx = Transaction(get_webpay_options())
        # PASO CRÍTICO: Le preguntamos a Transbank el estado real de ese token
        result = tx.commit(token)
        
        # Evaluamos la respuesta de Transbank
        # vci 'TSY' significa transacción exitosa, y response_code == 0 es aprobado
        if result['vci'] == 'TSY' and result['response_code'] == 0:
            # ¡EL PAGO ESTÁ APROBADO! 
            # Aquí es donde cambias el estado de tu pedido en la BD, vacías el carrito, etc.
            return render(request, 'tienda/pago_exitoso.html', {'result': result})
        else:
            # Pago rechazado (Fondos insuficientes, tarjeta inválida, etc.)
            return render(request, 'tienda/pago_rechazado.html', {'result': result})
            
    except Exception as e:
        print(f"Error al confirmar la transacción: {e}")
        return render(request, 'tienda/error.html', {'mensaje': 'Error al confirmar el estado del pago.'})