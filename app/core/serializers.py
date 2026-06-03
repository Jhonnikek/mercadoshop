from rest_framework import serializers
from .models import (
    Tienda, Producto, Pedido, DetallePedido, Usuario, Direccion, 
    Municipio, Departamento, Categoria, EstadoPedido, Rol, 
    DireccionCliente, Carrito, ItemCarrito, TrabajadorTienda, 
    TransaccionPasarela, TiendaAdmin
)

class DepartamentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Departamento
        fields = '__all__'

class MunicipioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Municipio
        fields = '__all__'

class DireccionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Direccion
        fields = '__all__'

class UsuarioSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)
    categorias_interes = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Categoria.objects.filter(estado=True),
        required=False,
    )

    class Meta:
        model = Usuario
        fields = ['id', 'username', 'email', 'password', 'tipo_usuario', 'documento', 'telefono', 'direccion_principal', 'rol_trabajador', 'estado_admin', 'categorias_interes']

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        categorias_interes = validated_data.pop('categorias_interes', [])
        usuario = Usuario(**validated_data)
        if password:
            usuario.set_password(password)
        usuario.save()
        if categorias_interes:
            usuario.categorias_interes.set(categorias_interes)
        return usuario

class TiendaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tienda
        fields = '__all__'

class ProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Producto
        fields = '__all__'

class DetallePedidoSerializer(serializers.ModelSerializer):
    class Meta:
        model = DetallePedido
        fields = ['id', 'producto', 'nombre_producto', 'precio_compra', 'cantidad', 'subtotal']
        read_only_fields = ['nombre_producto', 'precio_compra', 'subtotal']

class PedidoSerializer(serializers.ModelSerializer):
    detalles = DetallePedidoSerializer(many=True)

    class Meta:
        model = Pedido
        fields = [
            'id', 'cliente', 'direccion_cliente', 'numero_comprobante', 
            'subtotal', 'costo_envio', 'total', 'transaccion_pasarela', 
            'estado_pedido', 'fecha_actualizacion', 'detalles'
        ]
        read_only_fields = ['subtotal', 'total', 'fecha_actualizacion']

    def create(self, validated_data):
        detalles_data = validated_data.pop('detalles')
        subtotal = 0
        detalles_to_create = []

        for d_data in detalles_data:
            producto = d_data['producto']
            cantidad = d_data['cantidad']
            
            # Validar stock
            if producto.cantidad_stock < cantidad:
                raise serializers.ValidationError(
                    {"detalles": f"Stock insuficiente para el producto '{producto.descripcion_corta}'. Disponible: {producto.cantidad_stock}."}
                )
            
            # Descontar stock
            producto.cantidad_stock -= cantidad
            producto.save()

            item_subtotal = producto.precio_unitario * cantidad
            subtotal += item_subtotal

            detalles_to_create.append({
                'producto': producto,
                'nombre_producto': producto.descripcion_corta,
                'precio_compra': producto.precio_unitario,
                'cantidad': cantidad,
                'subtotal': item_subtotal
            })

        costo_envio = validated_data.get('costo_envio', 0)
        total = subtotal + costo_envio

        pedido = Pedido.objects.create(
            subtotal=subtotal,
            total=total,
            **validated_data
        )

        for item in detalles_to_create:
            DetallePedido.objects.create(pedido=pedido, **item)

        return pedido

class EstadoPedidoSerializer(serializers.ModelSerializer):
    class Meta:
        model = EstadoPedido
        fields = '__all__'

class RolSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rol
        fields = '__all__'

class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = '__all__'

class DireccionClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = DireccionCliente
        fields = '__all__'

class ItemCarritoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemCarrito
        fields = '__all__'

class CarritoSerializer(serializers.ModelSerializer):
    items = ItemCarritoSerializer(many=True, read_only=True)

    class Meta:
        model = Carrito
        fields = '__all__'

class TrabajadorTiendaSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrabajadorTienda
        fields = '__all__'

class TransaccionPasarelaSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransaccionPasarela
        fields = '__all__'

class TiendaAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = TiendaAdmin
        fields = '__all__'

