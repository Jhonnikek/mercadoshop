from django.urls import path
from . import views

urlpatterns = [
    path('productos/', views.crearProducto, name='crear_producto'),
]
