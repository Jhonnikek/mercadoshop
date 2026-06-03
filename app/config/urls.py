"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from core.views import (
    TiendaViewSet, ProductoViewSet, PedidoViewSet, UsuarioViewSet,
    test_dashboard, home, register_view, producto_detalle_view,
    perfil_settings_view, tienda_publico_view, inventario_trabajador_view,
    historial_pedidos_view, DepartamentoViewSet, MunicipioViewSet,
    DireccionViewSet,
    producto_crear_view, producto_editar_view, producto_eliminar_view,
    pedido_detalle_trabajador_view, pedido_detalle_cliente_view,
    admin_tiendas_view, admin_usuarios_view, catalogo_search_view,
    agregar_al_carrito_view, carrito_detalle_view, remover_del_carrito_view,
    actualizar_item_carrito_view, realizar_pedido_view, pedido_exitoso_view,
    admin_usuario_crear_view, admin_usuario_editar_view, admin_usuario_eliminar_view,
    admin_tienda_crear_view, admin_tienda_editar_view, admin_tienda_eliminar_view,
    admin_pedidos_view, admin_pedido_crear_view, admin_pedido_editar_view, admin_pedido_eliminar_view,
    EstadoPedidoViewSet, RolViewSet, CategoriaViewSet, DireccionClienteViewSet,
    CarritoViewSet, ItemCarritoViewSet, TrabajadorTiendaViewSet,
    TransaccionPasarelaViewSet, TiendaAdminViewSet
)

# Inicializar router de DRF
router = DefaultRouter()
router.register(r'tiendas', TiendaViewSet, basename='tienda')
router.register(r'productos', ProductoViewSet, basename='producto')
router.register(r'pedidos', PedidoViewSet, basename='pedido')
router.register(r'usuarios', UsuarioViewSet, basename='usuario')
router.register(r'departamentos', DepartamentoViewSet, basename='departamento')
router.register(r'municipios', MunicipioViewSet, basename='municipio')
router.register(r'direcciones', DireccionViewSet, basename='direccion')
router.register(r'estados-pedido', EstadoPedidoViewSet, basename='estadopedido')
router.register(r'roles', RolViewSet, basename='rol')
router.register(r'categorias', CategoriaViewSet, basename='categoria')
router.register(r'direcciones-cliente', DireccionClienteViewSet, basename='direccioncliente')
router.register(r'carritos', CarritoViewSet, basename='carrito')
router.register(r'items-carrito', ItemCarritoViewSet, basename='itemcarrito')
router.register(r'trabajadores-tienda', TrabajadorTiendaViewSet, basename='trabajadortienda')
router.register(r'transacciones', TransaccionPasarelaViewSet, basename='transaccion')
router.register(r'tiendas-admin', TiendaAdminViewSet, basename='tiendaadmin')


urlpatterns = [
    # Página de inicio del Marketplace
    path('', home, name='home'),

    # Panel de administración de Django
    path('admin/', admin.site.urls),
    
    # Endpoints de la API REST
    path('api/', include(router.urls)),
    
    # Autenticación JWT para la API
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Vistas de autenticación estándar de Django para pruebas locales
    path('login/', auth_views.LoginView.as_view(template_name='login_prueba.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/login/'), name='logout'),
    
    # Vista del panel de pruebas local
    path('dashboard/', test_dashboard, name='test_dashboard'),
    
    # Nuevas rutas dinámicas
    path('registro/', register_view, name='register'),
    path('producto/<int:pk>/', producto_detalle_view, name='producto_detalle'),
    path('configuracion/', perfil_settings_view, name='perfil_settings'),
    path('tienda/<int:pk>/', tienda_publico_view, name='tienda_publico'),
    path('inventario/', inventario_trabajador_view, name='inventario_trabajador'),
    path('pedidos/', historial_pedidos_view, name='historial_pedidos'),
    
    # Nuevas vistas para CRUD, pedidos y administración
    path('inventario/crear/', producto_crear_view, name='producto_crear'),
    path('inventario/editar/<int:pk>/', producto_editar_view, name='producto_editar'),
    path('inventario/eliminar/<int:pk>/', producto_eliminar_view, name='producto_eliminar'),
    path('pedidos/<int:pk>/detalle/', pedido_detalle_trabajador_view, name='pedido_detalle_trabajador'),
    path('pedidos/<int:pk>/seguimiento/', pedido_detalle_cliente_view, name='pedido_detalle_cliente'),
    path('admin-dashboard/tiendas/', admin_tiendas_view, name='admin_tiendas'),
    path('admin-dashboard/tiendas/crear/', admin_tienda_crear_view, name='admin_tienda_crear'),
    path('admin-dashboard/tiendas/editar/<int:pk>/', admin_tienda_editar_view, name='admin_tienda_editar'),
    path('admin-dashboard/tiendas/eliminar/<int:pk>/', admin_tienda_eliminar_view, name='admin_tienda_eliminar'),
    path('admin-dashboard/usuarios/', admin_usuarios_view, name='admin_usuarios'),
    path('admin-dashboard/usuarios/crear/', admin_usuario_crear_view, name='admin_usuario_crear'),
    path('admin-dashboard/usuarios/editar/<int:pk>/', admin_usuario_editar_view, name='admin_usuario_editar'),
    path('admin-dashboard/usuarios/eliminar/<int:pk>/', admin_usuario_eliminar_view, name='admin_usuario_eliminar'),
    path('admin-dashboard/pedidos/', admin_pedidos_view, name='admin_pedidos'),
    path('admin-dashboard/pedidos/crear/', admin_pedido_crear_view, name='admin_pedido_crear'),
    path('admin-dashboard/pedidos/editar/<int:pk>/', admin_pedido_editar_view, name='admin_pedido_editar'),
    path('admin-dashboard/pedidos/eliminar/<int:pk>/', admin_pedido_eliminar_view, name='admin_pedido_eliminar'),
    path('catalogo/', catalogo_search_view, name='catalogo'),
    
    # Rutas para el Carrito y Checkout
    path('carrito/', carrito_detalle_view, name='carrito_detalle'),
    path('carrito/agregar/<int:producto_id>/', agregar_al_carrito_view, name='agregar_al_carrito'),
    path('carrito/remover/<int:item_id>/', remover_del_carrito_view, name='remover_del_carrito'),
    path('carrito/actualizar/<int:item_id>/', actualizar_item_carrito_view, name='actualizar_item_carrito'),
    path('carrito/checkout/', realizar_pedido_view, name='realizar_pedido'),
    path('pedido/exitoso/<int:pk>/', pedido_exitoso_view, name='pedido_exitoso'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


