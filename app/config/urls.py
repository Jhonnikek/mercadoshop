"""
URL configuration for config project.
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from .views import api_root

urlpatterns = [
    path('admin/', admin.site.urls),
    path('panel/', include('panel_admin.urls')),
    path('api/', api_root, name='api_root'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/tiendas/', include('tiendas.urls')),
    path('api/clientes/', include('clientes.urls')),
    path('api-auth/', include('rest_framework.urls')),
]
