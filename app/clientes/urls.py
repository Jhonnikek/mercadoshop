from django.urls import path
from asgiref.sync import sync_to_async
from . import views

urlpatterns = [
    # ASYNC: Envolvemos las vistas DRF (@api_view) con sync_to_async como puente seguro.
    path('productos/', sync_to_async(views.listarProductos), name='listar_productos'),
    path('productos/<int:id>/', sync_to_async(views.obtenerProducto), name='obtener_producto'),
    path('tiendas/', sync_to_async(views.listarTiendas), name='listar_tiendas'),
]
