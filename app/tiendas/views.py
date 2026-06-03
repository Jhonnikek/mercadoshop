from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Producto
from .serializers import ProductoSerializer


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def crearProducto(request):
    """
    API REST para crear un producto.
    Consumida por la app de escritorio (Flutter Desktop).

    Recibe JSON: {"nombre": "Zapatos", "precio": 100, "stock": 50, "tienda": 1}
    Responde JSON: {"status": "success", "producto": {...}}
    """
    serializer = ProductoSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(
            {'status': 'success', 'producto': serializer.data},
            status=status.HTTP_201_CREATED,
        )
    return Response(
        {'status': 'error', 'errors': serializer.errors},
        status=status.HTTP_400_BAD_REQUEST,
    )
