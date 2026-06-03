from django.urls import path
from . import views

urlpatterns = [
    path('productos/', views.listarProductos, name='listar_productos'),
]
