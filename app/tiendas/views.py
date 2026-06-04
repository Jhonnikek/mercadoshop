from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Producto
from .serializers import ProductoSerializer


class CrearProductoView(generics.CreateAPIView):
    """
    API REST para crear un producto.
    Consumida por la app de escritorio (Flutter Desktop).
    """
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(
                {'status': 'success', 'producto': serializer.data},
                status=status.HTTP_201_CREATED,
                headers=headers
            )
        return Response(
            {'status': 'error', 'errors': serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )
