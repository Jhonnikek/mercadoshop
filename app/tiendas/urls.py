from django.urls import path

from . import views

urlpatterns = [
    path("productos/", views.ProductoListCreateView.as_view(), name="producto_list_create"),
    path("productos/<int:pk>/", views.ProductoDetailView.as_view(), name="producto_detail"),
    path("dashboard/", views.DashboardResumenView.as_view(), name="dashboard_resumen"),
]
