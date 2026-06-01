from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    Usuario, Departamento, Municipio, Direccion, EstadoPedido, Rol, Categoria,
    DireccionCliente, Carrito, Tienda, Producto, TrabajadorTienda, Pedido,
    DetallePedido, TransaccionPasarela, TiendaAdmin
)

class CustomUserAdmin(UserAdmin):
    model = Usuario
    list_display = ['username', 'email', 'tipo_usuario', 'is_staff', 'is_active']
    fieldsets = UserAdmin.fieldsets + (
        ('Información de Mercado Shop', {'fields': ('tipo_usuario', 'documento', 'telefono', 'direccion_principal', 'rol_trabajador', 'estado_admin', 'categorias_interes')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Información de Mercado Shop', {'fields': ('tipo_usuario', 'documento', 'telefono', 'direccion_principal', 'rol_trabajador', 'estado_admin', 'categorias_interes')}),
    )

# Registrar modelos
admin.site.register(Usuario, CustomUserAdmin)
admin.site.register(Departamento)
admin.site.register(Municipio)
admin.site.register(Direccion)
admin.site.register(EstadoPedido)
admin.site.register(Rol)
admin.site.register(Categoria)
admin.site.register(DireccionCliente)
admin.site.register(Carrito)
admin.site.register(Tienda)
admin.site.register(Producto)
admin.site.register(TrabajadorTienda)
admin.site.register(Pedido)
admin.site.register(DetallePedido)
admin.site.register(TransaccionPasarela)
admin.site.register(TiendaAdmin)

