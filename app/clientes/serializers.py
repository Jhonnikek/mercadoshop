from rest_framework import serializers
from tiendas.models import Producto
from panel_admin.models import Tienda


class TiendaPublicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tienda
        fields = ['id', 'nombre', 'direccion']


class ProductoListSerializer(serializers.ModelSerializer):
    tienda_nombre = serializers.CharField(source='tienda.nombre', read_only=True)
    tienda_id = serializers.IntegerField(source='tienda.id', read_only=True)

    class Meta:
        model = Producto
        fields = ['id', 'nombre', 'precio', 'stock', 'descripcion', 'tienda_id', 'tienda_nombre']
