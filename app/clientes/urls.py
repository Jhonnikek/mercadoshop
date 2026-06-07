from django.urls import path
from . import views

urlpatterns = [
    path('productos/', views.listarProductos, name='listar_productos'),
    path('productos/<int:id>/', views.obtenerProducto, name='obtener_producto'),
    path('tiendas/', views.listarTiendas, name='listar_tiendas'),
]
