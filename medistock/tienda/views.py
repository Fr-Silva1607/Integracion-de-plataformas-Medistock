import json
import random
import math
import time
import datetime
from django.shortcuts import render
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

# Transbank Webpay Plus
from transbank.common.options import WebpayOptions
from transbank.common.integration_type import IntegrationType
from transbank.common.integration_commerce_codes import IntegrationCommerceCodes
from transbank.common.integration_api_keys import IntegrationApiKeys
from transbank.webpay.webpay_plus.transaction import Transaction as WebpayTransaction

COMMERCE_CODE_TEST = IntegrationCommerceCodes.WEBPAY_PLUS
API_KEY_TEST = IntegrationApiKeys.WEBPAY

# aqui dice "wey, tengo los datos "
options = WebpayOptions(COMMERCE_CODE_TEST, API_KEY_TEST, IntegrationType.TEST)

# incializa la wea
tx = WebpayTransaction(options)

# vistas princpales
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

#logica de transback

@csrf_exempt
def webpay_iniciar(request):

    amount_raw = 0
    orden_id = None

    if request.method == 'POST' and request.body:
        try:
            payload = json.loads(request.body.decode('utf-8'))
            amount_raw = payload.get('amount')
            orden_id = payload.get('orden_id')
        except (ValueError, json.JSONDecodeError):
            pass
    else:
        amount_raw = request.GET.get('amount')
        orden_id = request.GET.get('orden_id')

    # Forzar entero limpio para el monto
    try:
        if amount_raw is not None:
            amount = int(round(float(amount_raw)))
        else:
            amount = 0
    except (ValueError, TypeError):
        amount = 0

    if amount <= 0:
        amount = 15500

    if not orden_id:
        orden_id = random.randint(10000, 99999)

    timestamp_unico = str(int(time.time()))[-4:]
    buy_order = f"MDS-{orden_id}-{timestamp_unico}"[:26]
    session_id = f"sess{orden_id}"[:26]

    # Ajuste de cabecera local para evitar fallos de handshake en redirección
    host = request.get_host()
    if 'localhost' in host:
        host = host.replace('localhost', '127.0.0.1')
    
    return_url = f"{request.scheme}://{host}/webpay-retorno/"

    print(f"--- CONFIGURANDO LLAMADA WEBPAY ---")
    print(f"Buy Order: {buy_order}")
    print(f"Amount: {amount} (Tipo: {type(amount)})")
    print(f"Session ID: {session_id}")
    print(f"Return URL: {return_url}")
    print(f"------------------------------------")

    try:
        # Usamos directamente el objeto 'tx' global ya instanciado correctamente arriba
        response = tx.create(buy_order, session_id, amount, return_url)

        if 'application/json' in request.headers.get('Accept', ''):
            return JsonResponse({
                'url': response['url'],
                'token': response['token'],
                'buy_order': buy_order,
            })

        return render(request, 'tienda/webpay_redirect.html', {
            'url': response['url'],
            'token': response['token'],
        })

    except Exception as e:
        import traceback
        print(f" Error crítico en Transbank: {str(e)}")
        traceback.print_exc() 
        
        error_msg = str(e)
        
        if 'application/json' in request.headers.get('Accept', ''):
            return JsonResponse({
                'success': False,
                'error': f'Error de Transbank: {error_msg}'
            }, status=400)
            
        return render(request, 'tienda/error.html', {
            'mensaje': f'No se pudo iniciar el pago: {error_msg}'
        })


@csrf_exempt
def webpay_retorno(request):
    #recibe si tansback dice que si si compro o no, no compro xd
    token = request.GET.get('token_ws') or request.POST.get('token_ws')

    if not token:
        return render(request, 'tienda/pago_rechazado.html', {
            'mensaje': 'Pago cancelado por el usuario o token ausente.',
            'result': None,
        })

    try:
        # Confirmamos la transacción usando el objeto 'tx' global
        result = tx.commit(token)

        # Transacción aprobada con éxito por el banco (response_code = 0)
        if result.get('response_code') == 0:
            return render(request, 'tienda/pago_exitoso.html', {'result': result})
        else:
            return render(request, 'tienda/pago_rechazado.html', {
                'mensaje': 'El pago fue rechazado por el banco.',
                'result': result,
            })

    except Exception as e:
        print(f"Error al confirmar transacción Transbank: {e}")
        return render(request, 'tienda/error.html', {
            'mensaje': f'Error al confirmar el pago: {str(e)}'
        })


#metodos carrito
@require_http_methods(["POST"])
@csrf_exempt
def api_calcular_total(request):
    #calcula iva
    try:
        payload = json.loads(request.body.decode('utf-8'))
        items = payload.get('items', [])

        if not isinstance(items, list) or not items:
            return JsonResponse({
                'success': False,
                'error': 'Debes enviar una lista de items con precio y cantidad'
            }, status=400)

        subtotal = 0
        for item in items:
            precio = float(item.get('precio', 0))
            cantidad = int(item.get('cantidad', 1))
            if precio < 0 or cantidad < 1:
                return JsonResponse({
                    'success': False,
                    'error': 'Precio o cantidad inválidos'
                }, status=400)
            subtotal += precio * cantidad

        iva = subtotal * 0.19
        total = subtotal + iva

        return JsonResponse({
            'success': True,
            'subtotal': round(subtotal, 2),
            'iva': round(iva, 2),
            'total': round(total, 2),
            'items_count': len(items),
        })

    except (ValueError, json.JSONDecodeError) as e:
        return JsonResponse({
            'success': False,
            'error': f'JSON inválido: {str(e)}'
        }, status=400)

#verifica api, muy que muy importante poruque dios mio cuantos erres tiene esta madreeeeeeeeee
@require_http_methods(["GET"])
def api_status(request):

    return JsonResponse({
        'status': 'online',
        'message': 'API de Medistock funcionando correctamente',
        'timestamp': datetime.datetime.now().isoformat()
    })

#cosnulta bbdd
@require_http_methods(["GET"])
def api_productos(request):

    import urllib.request
    import urllib.parse

    params = {'select': '*', 'order': 'nombre.asc'}

    categoria = request.GET.get('categoria')
    tipo_venta = request.GET.get('tipo_venta')
    max_precio = request.GET.get('max_precio')
    buscar = request.GET.get('buscar')

    if categoria:
        params['categoria'] = f'eq.{categoria}'
    if tipo_venta:
        params['tipo_venta'] = f'eq.{tipo_venta}'
    if max_precio:
        params['precio'] = f'lte.{max_precio}'
    if buscar:
        params['nombre'] = f'ilike.*{buscar}*'

    url = f"{settings.SUPABASE_URL.rstrip('/')}/rest/v1/productos?" + urllib.parse.urlencode(params)
    headers = {
        'apikey': settings.SUPABASE_KEY,
        'Authorization': f'Bearer {settings.SUPABASE_KEY}',
        'Accept': 'application/json',
    }

    try:
        req = urllib.request.Request(url, headers=headers, method='GET')
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode('utf-8'))
        return JsonResponse({'count': len(data), 'productos': data})
    except Exception as e:
        return JsonResponse({'error': str(e), 'productos': []}, status=500)
    #DASHBOARD AAAAAAAAAAAAAAAAAAA
def dashboard(request):
    return render(request, 'tienda/dashboard.html')
from django.http import JsonResponse
from supabase import create_client

SUPABASE_URL = "https://ljzypuiqebttfmmgzsqk.supabase.co"
SUPABASE_KEY = "sb_publishable_LM3_tYyHvBjdPQxqJwB-zA_u03mDQwR"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def api_dashboard(request):
    try:
        res = supabase.table('productos').select('*').execute()
        productos = res.data

        total_productos = len(productos)

        total_inventario = sum(p['precio'] * p['cantidad'] for p in productos)

        bajo_stock = len([p for p in productos if p['cantidad'] < 5])

        # categorías
        categorias = {}
        for p in productos:
            cat = p.get('categoria', 'Otros')
            categorias[cat] = categorias.get(cat, 0) + 1

        return JsonResponse({
            'total_productos': total_productos,
            'total_inventario': total_inventario,
            'bajo_stock': bajo_stock,
            'categorias': categorias
        })

    except Exception as e:
        return JsonResponse({'error': str(e)})