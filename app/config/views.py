from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

@api_view(['GET'])
@permission_classes([AllowAny])
def api_root(request):
    """
    Punto de entrada principal a la API.
    """
    return Response({
        "nombre": "MercadoShop API",
        "version": "1.0",
        "status": "online"
    })
