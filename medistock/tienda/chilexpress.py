import json
import urllib.request
import urllib.error

from django.conf import settings


def chilexpress_request(endpoint, body=None, method="POST"):
    """
    Cliente para consumir la API REST de Chilexpress.
    """

    url = f"{settings.CHILEXPRESS_BASE_URL}{endpoint}"

    headers = {
        "Content-Type": "application/json",
        "Ocp-Apim-Subscription-Key": settings.CHILEXPRESS_API_KEY,
    }

    data = None

    if body:
        data = json.dumps(body).encode("utf-8")

    request = urllib.request.Request(
        url,
        headers=headers,
        data=data,
        method=method
    )

    try:

        with urllib.request.urlopen(request, timeout=20) as response:

            return json.loads(response.read().decode())

    except urllib.error.HTTPError as e:

        return {
            "error": True,
            "status": e.code,
            "mensaje": e.reason
        }

    except Exception as e:

        return {
            "error": True,
            "mensaje": str(e)
        }
    
#cotizar

def cotizar_envio(
    origen,
    destino,
    peso,
    alto,
    ancho,
    largo,
    valor
):

    body = {

        "originCountyCode": origen,
        "destinationCountyCode": destino,

        "package": {

            "weight": str(peso),
            "height": str(alto),
            "width": str(ancho),
            "length": str(largo)

        },

        "productType": 3,
        "contentType": 1,
        "declaredWorth": str(valor),
        "deliveryTime": 0

    }

    return chilexpress_request(
        "/rating/api/v1.0/rates/courier",
        body
    )

#Valida Direcciones
def buscar_calles(comuna, calle):

    body = {

        "countyName": comuna,
        "streetName": calle,
        "pointsOfInterestEnabled": True,
        "streetNameEnabled": True,
        "roadType": 0

    }

    return chilexpress_request(
        "/georeference/api/v1.0/streets/search",
        body
    )