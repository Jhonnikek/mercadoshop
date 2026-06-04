from rest_framework import generics, status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Producto
from .serializers import ProductoSerializer


class CrearProductoView(generics.CreateAPIView):
    """
    API REST para crear un producto.
    """

    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        if not hasattr(self.request.user, "tienda"):
            raise ValidationError(
                {"tienda": "El usuario actual no tiene una tienda asociada."}
            )
        serializer.save(tienda=self.request.user.tienda)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            try:
                self.perform_create(serializer)
            except ValidationError as e:
                return Response(
                    {"status": "error", "errors": e.detail},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            headers = self.get_success_headers(serializer.data)
            return Response(
                {"status": "success", "producto": serializer.data},
                status=status.HTTP_201_CREATED,
                headers=headers,
            )
        return Response(
            {"status": "error", "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )
