from django.urls import path
from asgiref.sync import sync_to_async

from . import views

urlpatterns = [
    # ASYNC: Usamos sync_to_async como puente ya que DRF CBVs no son nativamente asíncronos.
    path("productos/", sync_to_async(views.ProductoListCreateView.as_view()), name="producto_list_create"),
    path("productos/<int:pk>/", sync_to_async(views.ProductoDetailView.as_view()), name="producto_detail"),
    path("dashboard/", sync_to_async(views.DashboardResumenView.as_view()), name="dashboard_resumen"),
]
