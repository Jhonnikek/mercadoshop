from django.urls import path
from . import views

urlpatterns = [
    path('productos/', views.CrearProductoView.as_view(), name='crear_producto'),
]
