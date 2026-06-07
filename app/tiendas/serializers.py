from rest_framework import serializers

from panel_admin.models import Tienda

from .models import Producto


class ProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Producto
        fields = ["id", "nombre", "precio", "stock", "descripcion", "tienda"]
        read_only_fields = ["tienda"]


class TiendaResumenSerializer(serializers.ModelSerializer):
    total_productos = serializers.IntegerField(read_only=True)
    total_stock = serializers.IntegerField(read_only=True)

    class Meta:
        model = Tienda
        fields = ["id", "nombre", "direccion", "activo", "total_productos", "total_stock"]
