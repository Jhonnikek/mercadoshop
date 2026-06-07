from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from . import views
from .forms import AdminLoginForm

urlpatterns = [
    path('login/', LoginView.as_view(template_name='panel_admin/login.html', authentication_form=AdminLoginForm), name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('', views.dashboard, name='dashboard'),
    path('tiendas/', views.gestionarTiendas, name='gestionar_tiendas'),
    path('tiendas/crear/', views.crearTiendaAjax, name='crear_tienda_ajax'),
    path('tiendas/<int:id>/editar/', views.editarTiendaAjax, name='editar_tienda_ajax'),
    path('tiendas/<int:id>/eliminar/', views.eliminarTiendaAjax, name='eliminar_tienda_ajax'),
    path('tiendas/<int:id>/detalle/', views.detalleTiendaAjax, name='detalle_tienda_ajax'),
    # AJAX endpoints para popups del dashboard
    path('ajax/productos/', views.listarProductosGlobalAjax, name='listar_productos_global_ajax'),
    path('ajax/tiendas/', views.listarTiendasGlobalAjax, name='listar_tiendas_global_ajax'),
]
