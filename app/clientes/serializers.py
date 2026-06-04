from rest_framework import serializers
from tiendas.models import Producto


class ProductoListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Producto
        fields = ['id', 'nombre', 'precio', 'stock', 'descripcion']
