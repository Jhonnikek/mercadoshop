from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from tiendas.models import Producto
from panel_admin.models import Tienda

from .serializers import ProductoListSerializer, TiendaPublicSerializer

# ASYNC: DRF @api_view no soporta nativamente async def.
# Las vistas se mantienen síncronas y se envuelven con sync_to_async en urls.py 
# como puente seguro para la compatibilidad con ASGI.

@api_view(["GET"])
@permission_classes([AllowAny])
def listarProductos(request):
    productos = Producto.objects.filter(tienda__activo=True)

    tienda_id = request.query_params.get('tienda')
    if tienda_id is not None:
        productos = productos.filter(tienda_id=tienda_id)

    serializer = ProductoListSerializer(productos, many=True)
    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([AllowAny])
def obtenerProducto(request, id):
    producto = get_object_or_404(Producto, id=id, tienda__activo=True)
    serializer = ProductoListSerializer(producto)
    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([AllowAny])
def listarTiendas(request):
    tiendas = Tienda.objects.filter(activo=True)
    serializer = TiendaPublicSerializer(tiendas, many=True)
    return Response(serializer.data)
