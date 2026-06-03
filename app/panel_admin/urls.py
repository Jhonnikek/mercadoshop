from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from . import views

urlpatterns = [
    path('login/', LoginView.as_view(template_name='panel_admin/login.html'), name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('', views.dashboard, name='dashboard'),
    path('tiendas/', views.gestionarTiendas, name='gestionar_tiendas'),
    path('tiendas/crear/', views.crearTiendaAjax, name='crear_tienda_ajax'),
    path('tiendas/<int:id>/editar/', views.editarTiendaAjax, name='editar_tienda_ajax'),
    path('tiendas/<int:id>/eliminar/', views.eliminarTiendaAjax, name='eliminar_tienda_ajax'),
]
