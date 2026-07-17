"""
API REST de MediStock
Endpoints públicos para consumir productos desde clientes externos
(apps móviles, ESP32, dashboards, etc). 
"""
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.conf import settings
import json
import urllib.request
import urllib.parse
import urllib.error
from . import chilexpress
import requests


def _supabase_request(endpoint, method='GET', params=None, body=None):
    """Helper para hacer peticiones HTTP a Supabase REST."""
    base = settings.SUPABASE_URL.rstrip('/')
    url = f"{base}/rest/v1/{endpoint}"

    if params:
        url += '?' + urllib.parse.urlencode(params)

    headers = {
        'apikey': settings.SUPABASE_SERVER_KEY,
        'Authorization': f'Bearer {settings.SUPABASE_SERVER_KEY}',
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    }

    data = None
    if body is not None:
        data = json.dumps(body).encode('utf-8')

    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            content = resp.read().decode('utf-8')
            return json.loads(content) if content else []
    except urllib.error.HTTPError as e:
        return {'error': f'HTTP {e.code}: {e.reason}'}
    except Exception as e:
        return {'error': str(e)}


@require_http_methods(['GET'])
def api_productos(request):
    """
    GET /api/productos/
    Lista todos los productos. Soporta filtros vía query params:
      - ?categoria=insumos
      - ?tipo_venta=personal
      - ?max_precio=50000
      - ?buscar=mascarilla
    Devuelve JSON con los productos.
    """
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

    data = _supabase_request('productos', params=params)

    if isinstance(data, dict) and 'error' in data:
        return JsonResponse(data, status=500)

    return JsonResponse({
        'count': len(data),
        'productos': data,
    })


@require_http_methods(['GET'])
def api_producto_detalle(request, producto_id):
    """
    GET /api/productos/<id>/
    Detalle de un producto.
    """
    params = {'select': '*', 'id': f'eq.{producto_id}'}
    data = _supabase_request('productos', params=params)

    if isinstance(data, dict) and 'error' in data:
        return JsonResponse(data, status=500)

    if not data:
        return JsonResponse({'error': 'Producto no encontrado'}, status=404)

    return JsonResponse(data[0])


@require_http_methods(['GET'])
def api_categorias(request):
    """
    GET /api/categorias/
    Lista única de categorías disponibles.
    """
    data = _supabase_request('productos', params={'select': 'categoria'})

    if isinstance(data, dict) and 'error' in data:
        return JsonResponse(data, status=500)

    categorias = sorted({p['categoria'] for p in data if p.get('categoria')})
    return JsonResponse({'categorias': categorias})

@require_http_methods(['GET'])
def api_stock(request):
    """
    GET /api/productos/stock/

    Parámetros opcionales:
      ?estado=bajo
      ?minimo=5

    Devuelve únicamente información del stock de los productos.
    """

    data = _supabase_request(
        'productos',
        params={'select': 'id,nombre,cantidad'}
    )

    if isinstance(data, dict) and 'error' in data:
        return JsonResponse(data, status=500)

    minimo = int(request.GET.get('minimo', 5))
    estado = request.GET.get('estado')

    productos = []

    for p in data:

        cantidad = p.get('cantidad', 0)

        if cantidad <= 0:
            estado_stock = "Sin Stock"
        elif cantidad <= minimo:
            estado_stock = "Stock Bajo"
        else:
            estado_stock = "Disponible"

        if estado == "bajo" and estado_stock != "Stock Bajo":
            continue

        productos.append({
            "id": p["id"],
            "nombre": p["nombre"],
            "stock": cantidad,
            "estado": estado_stock
        })

    return JsonResponse({
        "count": len(productos),
        "productos": productos
    })      

@csrf_exempt
@require_http_methods(['POST'])
def api_chilexpress_cotizar(request):
    """
    POST /api/chilexpress/cotizar/

    Cotiza un envío utilizando la API REST de Chilexpress.
    """

    try:
        body = json.loads(request.body)

        payload = {

            "originCountyCode": body["origen"],
            "destinationCountyCode": body["destino"],

            "package": {

                "weight": str(body["peso"]),
                "height": str(body["alto"]),
                "width": str(body["ancho"]),
                "length": str(body["largo"])

            },

            "productType": 3,
            "contentType": 1,
            "declaredWorth": str(body["valor"]),
            "deliveryTime": 0

        }

        url = "http://testservices.wschilexpress.com/rating/api/v1.0/rates/courier"

        req = urllib.request.Request(

            url,

            data=json.dumps(payload).encode(),

            headers={
                "Content-Type": "application/json"
            },

            method="POST"

        )

        with urllib.request.urlopen(req, timeout=20) as response:

            respuesta = json.loads(response.read().decode())

            return JsonResponse(respuesta)

    except Exception as e:

        return JsonResponse({

            "error": str(e)

        }, status=500)
    
@require_http_methods(["GET"])
def api_chilexpress_coberturas(request):

    url = "https://testservices.wschilexpress.com/georeference/api/v1.0/coverage-areas"

    try:

        response = requests.get(url, timeout=10)

        return JsonResponse(response.json(), safe=False)

    except Exception as e:

        return JsonResponse({
            "error": str(e)
        }, status=500)   

@csrf_exempt
@require_http_methods(['POST'])
def api_cotizar_envio(request):
    """
    POST /api/chilexpress/cotizar/

    Cotiza un envío utilizando la API de Chilexpress.
    """

    try:
        body = json.loads(request.body)

    except json.JSONDecodeError:
        return JsonResponse(
            {"error": "JSON inválido"},
            status=400
        )

    resultado = chilexpress.cotizar_envio(

        origen=body.get("origen"),
        destino=body.get("destino"),
        peso=body.get("peso"),
        alto=body.get("alto"),
        ancho=body.get("ancho"),
        largo=body.get("largo"),
        valor=body.get("valor")

    )

    return JsonResponse(resultado)

@csrf_exempt
@require_http_methods(['POST'])
def api_validar_direccion(request):
    """
    POST /api/chilexpress/validar-direccion/

    Busca una calle utilizando la API de Chilexpress.
    """

    try:
        body = json.loads(request.body)

    except json.JSONDecodeError:
        return JsonResponse(
            {"error": "JSON inválido"},
            status=400
        )

    resultado = chilexpress.buscar_calles(

        comuna=body.get("comuna"),
        calle=body.get("calle")

    )

    return JsonResponse(resultado)  

@csrf_exempt
@require_http_methods(['POST'])
def api_crear_orden(request):
    """
    POST /api/ordenes/
    Crea una orden a partir de un JSON.
    Body esperado:
      {
        "usuario_id": 1 | null,
        "empresa_id": null | 1,
        "items": [{"id": 1, "nombre": "...", "precio": 1000, "cantidad": 2}],
        "tipo_orden": "personal" | "empresa"
      }
    """
    try:
        body = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'JSON inválido'}, status=400)

    items = body.get('items', [])
    if not items:
        return JsonResponse({'error': 'La orden debe tener al menos un item'}, status=400)

    # Calcular totales en el servidor (no confiar en cliente)
    subtotal = sum(float(i.get('precio', 0)) * int(i.get('cantidad', 0)) for i in items)
    iva = round(subtotal * 0.19, 2)
    total = round(subtotal + iva, 2)

    orden = {
        'usuario_id': body.get('usuario_id'),
        'empresa_id': body.get('empresa_id'),
        'estado': 'pendiente',
        'items': items,
        'total_items': len(items),
        'subtotal': subtotal,
        'iva': iva,
        'total': total,
        'tipo_orden': body.get('tipo_orden', 'personal'),
        'metodo_pago': body.get('metodo_pago', 'transbank'),
    }

    data = _supabase_request('ordenes', method='POST', body=orden)

    if isinstance(data, dict) and 'error' in data:
        return JsonResponse(data, status=500)

    return JsonResponse({'ok': True, 'orden': data[0] if data else orden}, status=201)


@require_http_methods(['GET'])
def api_health(request):
    """
    GET /api/health/
    Health-check del API.
    """
    return JsonResponse({
        'status': 'ok',
        'service': 'medistock-api',
        'version': '1.0',
    })

@require_http_methods(['GET'])
def api_ordenes(request):
    """
    GET /api/ordenes/
    Lista todas las órdenes
    """
    data = _supabase_request('ordenes', params={'select': '*'})

    if isinstance(data, dict) and 'error' in data:
        return JsonResponse(data, status=500)

    return JsonResponse({
        'ordenes': data
    })