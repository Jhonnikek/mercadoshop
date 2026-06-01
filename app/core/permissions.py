from rest_framework import permissions
from .models import TrabajadorTienda

class EsAdministrador(permissions.BasePermission):
    """
    Permite acceso completo a administradores de la plataforma o superusuarios.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.tipo_usuario == 'ADMIN' or request.user.is_superuser
        )


class EsTrabajadorDeTienda(permissions.BasePermission):
    """
    Permite acceso a trabajadores si están vinculados a la tienda específica.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.tipo_usuario == 'TRABAJADOR'

    def has_object_permission(self, request, view, obj):
        # Obtener las tiendas a las que está vinculado el trabajador
        tiendas_vinculadas = TrabajadorTienda.objects.filter(trabajador=request.user).values_list('tienda_id', flat=True)
        
        # Si el objeto es una Tienda
        if hasattr(obj, 'id') and obj.__class__.__name__ == 'Tienda':
            return obj.id in tiendas_vinculadas
        
        # Si el objeto es un Producto
        if hasattr(obj, 'tienda'):
            return obj.tienda.id in tiendas_vinculadas
            
        # Si el objeto es un Pedido (debe tener detalles con productos de la tienda)
        if obj.__class__.__name__ == 'Pedido':
            return obj.detalles.filter(producto__tienda_id__in=tiendas_vinculadas).exists()
            
        return False


class EsClientePropietario(permissions.BasePermission):
    """
    Permite acceso a clientes solo para sus propios datos (e.g., pedidos propios).
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.tipo_usuario == 'CLIENTE'

    def has_object_permission(self, request, view, obj):
        if hasattr(obj, 'cliente'):
            return obj.cliente == request.user
        return False
