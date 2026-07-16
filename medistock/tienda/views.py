import json
import random
import math
import time
import datetime
import urllib.error
import urllib.parse
import urllib.request
from django.shortcuts import render
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

TRANSBANK_AVAILABLE = False
try:
    from transbank.common.options import WebpayOptions
    from transbank.common.integration_type import IntegrationType
    from transbank.common.integration_commerce_codes import IntegrationCommerceCodes
    from transbank.common.integration_api_keys import IntegrationApiKeys
    from transbank.webpay.webpay_plus.transaction import Transaction as WebpayTransaction

    COMMERCE_CODE_TEST = IntegrationCommerceCodes.WEBPAY_PLUS
    API_KEY_TEST = IntegrationApiKeys.WEBPAY
    options = WebpayOptions(COMMERCE_CODE_TEST, API_KEY_TEST, IntegrationType.TEST)
    tx = WebpayTransaction(options)
    TRANSBANK_AVAILABLE = True
except ImportError:
    tx = None


def _supabase_server_request(endpoint, method='GET', params=None, body=None):
    """Server-side helper for Supabase REST operations."""
    base = settings.SUPABASE_URL.rstrip('/')
    url = f"{base}/rest/v1/{endpoint}"

    if params:
        url += '?' + urllib.parse.urlencode(params)

    server_key = getattr(settings, 'SUPABASE_SERVER_KEY', '') or settings.SUPABASE_KEY
    headers = {
        'apikey': server_key,
        'Authorization': f'Bearer {server_key}',
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Prefer': 'return=representation',
    }

    data = None
    if body is not None:
        data = json.dumps(body).encode('utf-8')

    request = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            content = response.read().decode('utf-8')
            return json.loads(content) if content else []
    except urllib.error.HTTPError as error:
        detail = error.read().decode('utf-8') if error.fp else error.reason
        return {'error': f'HTTP {error.code}: {detail}'}
    except Exception as error:
        return {'error': str(error)}


def _extract_order_id_from_buy_order(buy_order):
    """Extract original order id from Webpay buy_order format MDS-<id>-<suffix>."""
    if not buy_order or not buy_order.startswith('MDS-'):
        return None

    parts = buy_order.split('-')
    if len(parts) < 3:
        return None

    try:
        return int(parts[1])
    except (TypeError, ValueError):
        return None


def _load_order_for_payment(orden_id):
    data = _supabase_server_request(
        'ordenes',
        params={
            'select': 'id,estado,items',
            'id': f'eq.{orden_id}',
            'limit': 1,
        },
    )
    if isinstance(data, dict) and 'error' in data:
        raise RuntimeError(data['error'])
    if not data:
        raise RuntimeError(f'Orden {orden_id} no encontrada en Supabase')
    return data[0]


def _build_stock_updates(items):
    updates = []

    for item in items:
        producto_id = item.get('id')
        cantidad_vendida = int(item.get('cantidad', 0) or 0)
        if not producto_id or cantidad_vendida <= 0:
            raise RuntimeError('La orden contiene un item inválido para descontar stock')

        producto = _supabase_server_request(
            'productos',
            params={
                'select': 'id,nombre,cantidad',
                'id': f'eq.{producto_id}',
                'limit': 1,
            },
        )

        if isinstance(producto, dict) and 'error' in producto:
            raise RuntimeError(producto['error'])
        if not producto:
            raise RuntimeError(f'Producto {producto_id} no encontrado')

        producto_actual = producto[0]
        stock_actual = int(producto_actual.get('cantidad') or 0)
        if stock_actual < cantidad_vendida:
            raise RuntimeError(
                f'Stock insuficiente para {producto_actual.get("nombre") or producto_id}. '
                f'Disponible: {stock_actual}, solicitado: {cantidad_vendida}'
            )

        updates.append({
            'id': producto_id,
            'nombre': producto_actual.get('nombre'),
            'stock_actual': stock_actual,
            'cantidad_vendida': cantidad_vendida,
            'nuevo_stock': stock_actual - cantidad_vendida,
        })

    return updates


def _mark_order_paid_and_discount_stock(orden_id):
    orden = _load_order_for_payment(orden_id)
    estado_actual = (orden.get('estado') or '').lower()
    if estado_actual == 'pagada':
        return {
            'orden_id': orden_id,
            'already_processed': True,
            'productos_actualizados': [],
        }

    items = orden.get('items') or []
    if not items:
        raise RuntimeError(f'La orden {orden_id} no tiene items para descontar stock')

    updates = _build_stock_updates(items)

    for update in updates:
        result = _supabase_server_request(
            'productos',
            method='PATCH',
            params={'id': f'eq.{update["id"]}'},
            body={'cantidad': update['nuevo_stock']},
        )
        if isinstance(result, dict) and 'error' in result:
            raise RuntimeError(result['error'])

    orden_result = _supabase_server_request(
        'ordenes',
        method='PATCH',
        params={'id': f'eq.{orden_id}'},
        body={'estado': 'pagada'},
    )
    if isinstance(orden_result, dict) and 'error' in orden_result:
        raise RuntimeError(orden_result['error'])

    return {
        'orden_id': orden_id,
        'already_processed': False,
        'productos_actualizados': updates,
    }

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
        if not TRANSBANK_AVAILABLE or tx is None:
            raise RuntimeError('Módulo Transbank no disponible. No se puede iniciar pago.')

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
        if not TRANSBANK_AVAILABLE or tx is None:
            raise RuntimeError('Módulo Transbank no disponible. No se puede confirmar pago.')

        result = tx.commit(token)

        # Transacción aprobada con éxito por el banco (response_code = 0)
        if result.get('response_code') == 0:
            stock_result = None
            stock_error = None
            orden_id = _extract_order_id_from_buy_order(result.get('buy_order'))

            if orden_id is not None:
                try:
                    stock_result = _mark_order_paid_and_discount_stock(orden_id)
                except Exception as stock_exception:
                    stock_error = str(stock_exception)
                    print(f'Error descontando stock para orden {orden_id}: {stock_error}')
            else:
                stock_error = 'No se pudo determinar la orden asociada al pago confirmado.'

            return render(request, 'tienda/pago_exitoso.html', {
                'result': result,
                'stock_result': stock_result,
                'stock_error': stock_error,
            })
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
        'apikey': settings.SUPABASE_SERVER_KEY,
        'Authorization': f'Bearer {settings.SUPABASE_SERVER_KEY}',
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

SUPABASE_URL = getattr(settings, 'SUPABASE_URL', None)
SUPABASE_SERVER_KEY = getattr(settings, 'SUPABASE_SERVER_KEY', None)
SUPABASE_CLIENT = None

if SUPABASE_URL and SUPABASE_SERVER_KEY:
    try:
        from supabase import create_client
        SUPABASE_CLIENT = create_client(SUPABASE_URL, SUPABASE_SERVER_KEY)
    except ImportError:
        SUPABASE_CLIENT = None


def api_dashboard(request):
    if SUPABASE_CLIENT is None:
        return JsonResponse({'error': 'Supabase no está disponible. Configure SUPABASE_URL y SUPABASE_SERVER_KEY/SUPABASE_SECRET_KEY.'}, status=500)

    try:
        res = SUPABASE_CLIENT.table('productos').select('*').execute()
        productos = res.data or []

        total_productos = len(productos)

        total_inventario = sum((p.get('precio') or 0) * (p.get('cantidad') or 0) for p in productos)

        bajo_stock = len([p for p in productos if (p.get('cantidad') or 0) < 5])

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