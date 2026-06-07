from django.db.models import Count, Sum
from rest_framework import generics, status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Producto
from .serializers import ProductoSerializer, TiendaResumenSerializer


class TiendaMixin:
    """Ensure the authenticated user has a tienda and scope querysets to it."""

    permission_classes = [IsAuthenticated]

    def get_tienda(self):
        if not hasattr(self.request.user, "tienda"):
            raise ValidationError(
                {"tienda": "El usuario actual no tiene una tienda asociada."}
            )
        return self.request.user.tienda

    def get_queryset(self):
        return Producto.objects.filter(tienda=self.get_tienda())


class ProductoListCreateView(TiendaMixin, generics.ListCreateAPIView):
    serializer_class = ProductoSerializer

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.filter_queryset(self.get_queryset())
        except ValidationError as e:
            return Response(
                {"status": "error", "errors": e.detail},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = self.get_serializer(queryset, many=True)
        return Response(
            {"status": "success", "productos": serializer.data},
            status=status.HTTP_200_OK,
        )

    def perform_create(self, serializer):
        serializer.save(tienda=self.get_tienda())

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


class ProductoDetailView(TiendaMixin, generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ProductoSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(
            {"status": "success", "producto": serializer.data},
            status=status.HTTP_200_OK,
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"status": "success", "producto": serializer.data},
                status=status.HTTP_200_OK,
            )
        return Response(
            {"status": "error", "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response(
            {"status": "success", "mensaje": "Producto eliminado correctamente."},
            status=status.HTTP_200_OK,
        )


class DashboardResumenView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        if not hasattr(request.user, "tienda"):
            return Response(
                {"status": "error", "errors": {"tienda": "El usuario actual no tiene una tienda asociada."}},
                status=status.HTTP_400_BAD_REQUEST,
            )

        tienda = request.user.tienda
        aggregates = tienda.productos.aggregate(
            total_productos=Count("id"),
            total_stock=Sum("stock"),
        )

        tienda.total_productos = aggregates["total_productos"]
        tienda.total_stock = aggregates["total_stock"] or 0

        serializer = TiendaResumenSerializer(tienda)
        return Response(
            {"status": "success", "dashboard": serializer.data},
            status=status.HTTP_200_OK,
        )
