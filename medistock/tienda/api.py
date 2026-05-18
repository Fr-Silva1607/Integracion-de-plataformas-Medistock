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


def _supabase_request(endpoint, method='GET', params=None, body=None):
    """Helper para hacer peticiones HTTP a Supabase REST."""
    base = settings.SUPABASE_URL.rstrip('/')
    url = f"{base}/rest/v1/{endpoint}"

    if params:
        url += '?' + urllib.parse.urlencode(params)

    headers = {
        'apikey': settings.SUPABASE_KEY,
        'Authorization': f'Bearer {settings.SUPABASE_KEY}',
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