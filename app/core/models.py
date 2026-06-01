from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError

class Departamento(models.Model):
    nombre = models.CharField(max_length=255)
    codigo_dane = models.CharField(max_length=255)

    def __str__(self):
        return self.nombre

    class Meta:
        db_table = 'TDepartamento'


class Municipio(models.Model):
    departamento = models.ForeignKey(Departamento, on_delete=models.CASCADE, related_name='municipios')
    nombre = models.CharField(max_length=255)
    codigo_dane = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.nombre} ({self.departamento.nombre})"

    class Meta:
        db_table = 'TMunicipio'


class Direccion(models.Model):
    nomenclatura = models.CharField(max_length=255)
    barrio = models.CharField(max_length=255)
    notas_adicionales = models.CharField(max_length=255, null=True, blank=True)
    codigo_postal = models.CharField(max_length=255, null=True, blank=True)
    municipio = models.ForeignKey(Municipio, on_delete=models.CASCADE, related_name='direcciones')

    def __str__(self):
        return f"{self.nomenclatura}, {self.barrio} - {self.municipio.nombre}"

    class Meta:
        db_table = 'TDireccion'


class EstadoPedido(models.Model):
    nombre_estado = models.CharField(max_length=255)

    def __str__(self):
        return self.nombre_estado

    class Meta:
        db_table = 'TEstadoPedido'


class Rol(models.Model):
    nombre = models.CharField(max_length=255)
    descripcion = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.nombre

    class Meta:
        db_table = 'TRoles'
        verbose_name_plural = "Roles"


class Categoria(models.Model):
    nombre_categoria = models.CharField(max_length=255)
    categoria_padre = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='subcategorias')
    estado = models.BooleanField(default=True)

    def __str__(self):
        if self.categoria_padre:
            return f"{self.categoria_padre} > {self.nombre_categoria}"
        return self.nombre_categoria

    class Meta:
        db_table = 'TCategoria'


class Usuario(AbstractUser):
    TIPO_USUARIO_CHOICES = (
        ('ADMIN', 'Administrador de Plataforma'),
        ('TRABAJADOR', 'Trabajador de Tienda'),
        ('CLIENTE', 'Cliente'),
    )
    
    tipo_usuario = models.CharField(max_length=20, choices=TIPO_USUARIO_CHOICES, default='CLIENTE')
    documento = models.CharField(max_length=50, null=True, blank=True)
    telefono = models.CharField(max_length=50, null=True, blank=True)
    categorias_interes = models.ManyToManyField(Categoria, blank=True, related_name='clientes_interesados')
    
    # Específico para clientes (de TUsuarioCliente)
    direccion_principal = models.ForeignKey(Direccion, on_delete=models.SET_NULL, null=True, blank=True, related_name='usuarios_cliente')
    
    # Específico para trabajadores (de TTrabajador)
    rol_trabajador = models.ForeignKey(Rol, on_delete=models.SET_NULL, null=True, blank=True, related_name='trabajadores')
    
    # Específico para administradores (de TUsuarioAdmin)
    estado_admin = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return f"{self.username} ({self.get_tipo_usuario_display()})"

    class Meta:
        db_table = 'TUsuario'


class DireccionCliente(models.Model):
    cliente = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='direcciones_entrega')
    direccion = models.ForeignKey(Direccion, on_delete=models.CASCADE)
    etiqueta = models.CharField(max_length=255, null=True, blank=True) # e.g. "Casa", "Oficina"
    nombre_recibidor = models.CharField(max_length=255)
    telefono_recibidor = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.etiqueta or 'Dirección'} - Recibe: {self.nombre_recibidor}"

    class Meta:
        db_table = 'TDireccionCliente'


class Carrito(models.Model):
    cliente = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='carritos')
    estado = models.CharField(max_length=255) # e.g. "Activo", "Abandonado", "Convertido"
    fecha_ultima_actualizacion = models.DateTimeField(auto_now=True)
    fecha_expiracion = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Carrito {self.id} - Cliente: {self.cliente.username} ({self.estado})"

    class Meta:
        db_table = 'TCarrito'


class Tienda(models.Model):
    nombre_comercial = models.CharField(max_length=255)
    descripcion = models.TextField(null=True, blank=True)
    url_logo = models.CharField(max_length=255, null=True, blank=True)
    correo_atencion = models.EmailField(max_length=255)
    telefono_atencion = models.CharField(max_length=255)
    razon_social = models.CharField(max_length=255)
    direccion = models.ForeignKey(Direccion, on_delete=models.SET_NULL, null=True, blank=True)
    codigo_postal = models.CharField(max_length=255, null=True, blank=True)
    estado_tienda = models.CharField(max_length=50) # e.g. "Activa", "Inactiva"
    plan_id = models.IntegerField(null=True, blank=True) # nPlanFK
    fecha_vencimiento_suscripcion = models.DateTimeField(null=True, blank=True)
    categorias = models.ManyToManyField(Categoria, blank=True, related_name='tiendas')

    def __str__(self):
        return self.nombre_comercial

    class Meta:
        db_table = 'TTiendas'


class Producto(models.Model):
    tienda = models.ForeignKey(Tienda, on_delete=models.CASCADE, related_name='productos')
    descripcion_corta = models.CharField(max_length=255)
    descripcion_larga = models.TextField(null=True, blank=True)
    url_imagen_principal = models.CharField(max_length=255, null=True, blank=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, blank=True, related_name='productos')
    especificaciones = models.JSONField(null=True, blank=True)
    precio_unitario = models.DecimalField(max_digits=19, decimal_places=4)
    cantidad_stock = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.descripcion_corta} - {self.tienda.nombre_comercial}"

    class Meta:
        db_table = 'TProductos'


class TrabajadorTienda(models.Model):
    tienda = models.ForeignKey(Tienda, on_delete=models.CASCADE, related_name='trabajadores')
    trabajador = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='trabajos_tienda')

    def clean(self):
        if self.trabajador.tipo_usuario != 'TRABAJADOR':
            raise ValidationError({'trabajador': "El usuario asociado debe ser de tipo TRABAJADOR."})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.trabajador.username} -> {self.tienda.nombre_comercial}"

    class Meta:
        db_table = 'TTrabajadorTienda'
        verbose_name = "Trabajador de Tienda"
        verbose_name_plural = "Trabajadores de Tiendas"
        unique_together = ('tienda', 'trabajador')


class Pedido(models.Model):
    cliente = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='pedidos')
    direccion_cliente = models.ForeignKey(DireccionCliente, on_delete=models.SET_NULL, null=True, blank=True)
    numero_comprobante = models.CharField(max_length=255, unique=True)
    subtotal = models.DecimalField(max_digits=19, decimal_places=4)
    costo_envio = models.DecimalField(max_digits=19, decimal_places=4)
    total = models.DecimalField(max_digits=19, decimal_places=4)
    transaccion_pasarela = models.ForeignKey('TransaccionPasarela', on_delete=models.SET_NULL, null=True, blank=True, related_name='pedidos_asociados')
    estado_pedido = models.ForeignKey(EstadoPedido, on_delete=models.PROTECT, related_name='pedidos')
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Pedido {self.numero_comprobante} - Total: {self.total}"

    class Meta:
        db_table = 'TPedido'


class DetallePedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey(Producto, on_delete=models.SET_NULL, null=True, blank=True)
    nombre_producto = models.CharField(max_length=255)
    precio_compra = models.DecimalField(max_digits=19, decimal_places=4)
    cantidad = models.IntegerField()
    subtotal = models.DecimalField(max_digits=19, decimal_places=4)

    def __str__(self):
        return f"{self.cantidad}x {self.nombre_producto} en Pedido {self.pedido.numero_comprobante}"

    class Meta:
        db_table = 'TDetallePedido'


class TransaccionPasarela(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='transacciones')
    nombre_pasarela = models.CharField(max_length=255)
    id_transaccion_externa = models.CharField(max_length=255)
    metodo_pago = models.CharField(max_length=255)
    franquicia = models.CharField(max_length=50, null=True, blank=True)
    ultimos_4_digitos = models.CharField(max_length=4, null=True, blank=True)
    cuotas = models.IntegerField(null=True, blank=True)
    valor_transaccion = models.DecimalField(max_digits=19, decimal_places=4)
    estado_transaccion = models.CharField(max_length=255)
    codigo_aprobacion_banco = models.CharField(max_length=255, null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    raw_response = models.JSONField(null=True, blank=True)

    def __str__(self):
        return f"Transacción {self.id_transaccion_externa} ({self.estado_transaccion})"

    class Meta:
        db_table = 'TTransaccionPasarela'


class TiendaAdmin(models.Model):
    nombre = models.CharField(max_length=255)
    direccion = models.CharField(max_length=255)
    telefono = models.CharField(max_length=255)
    estado = models.CharField(max_length=50)

    def __str__(self):
        return self.nombre

    class Meta:
        db_table = 'TTiendaAdmin'

class ItemCarrito(models.Model):
    carrito = models.ForeignKey(Carrito, on_delete=models.CASCADE, related_name='items')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.cantidad}x {self.producto.descripcion_corta} en Carrito {self.carrito.id}"

    @property
    def get_item_price(self):
        return float(self.producto.precio_unitario) * self.cantidad

    class Meta:
        db_table = 'TItemCarrito'


