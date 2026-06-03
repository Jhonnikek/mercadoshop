from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from tiendas.models import Producto
from .serializers import ProductoListSerializer


@api_view(['GET'])
@permission_classes([AllowAny])
def listarProductos(request):
    """
    API REST para listar todos los productos del catálogo.
    Consumida por la app móvil (Flutter Android).

    Responde JSON: [{"id": 1, "nombre": "Zapatos", "precio": 100, "stock": 50}, ...]
    """
    productos = Producto.objects.all()
    serializer = ProductoListSerializer(productos, many=True)
    return Response(serializer.data)
