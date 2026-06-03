from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from .models import Tienda, Producto, Pedido, Usuario, TrabajadorTienda, Categoria, EstadoPedido, DireccionCliente, Carrito, ItemCarrito, DetallePedido
from .serializers import (
    TiendaSerializer, ProductoSerializer, PedidoSerializer, 
    UsuarioSerializer
)
from .permissions import EsAdministrador, EsTrabajadorDeTienda, EsClientePropietario


def _save_uploaded_media(uploaded_file, folder):
    if not uploaded_file:
        return ''

    storage = FileSystemStorage(location=settings.MEDIA_ROOT, base_url=settings.MEDIA_URL)
    filename = storage.save(f"{folder}/{uploaded_file.name}", uploaded_file)
    return storage.url(filename)

class TiendaViewSet(viewsets.ModelViewSet):
    queryset = Tienda.objects.all()
    serializer_class = TiendaSerializer

    def get_permissions(self):
        if self.action in ['create', 'destroy']:
            # Solo administradores pueden crear o eliminar tiendas
            permission_classes = [EsAdministrador]
        elif self.action in ['update', 'partial_update']:
            # Administradores o trabajadores de esa tienda específica
            permission_classes = [EsAdministrador | EsTrabajadorDeTienda]
        else:
            # Cualquiera autenticado puede listar/ver
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Tienda.objects.none()
        
        # Superusuario o administrador global ven todas
        if user.is_superuser or user.tipo_usuario == 'ADMIN':
            return Tienda.objects.all()
            
        # Trabajadores ven solo su(s) tienda(s) vinculada(s)
        if user.tipo_usuario == 'TRABAJADOR':
            tiendas_ids = TrabajadorTienda.objects.filter(trabajador=user).values_list('tienda_id', flat=True)
            return Tienda.objects.filter(id__in=tiendas_ids)
            
        # Clientes ven todas las tiendas activas
        return Tienda.objects.filter(estado_tienda='Activa')


class ProductoViewSet(viewsets.ModelViewSet):
    queryset = Producto.objects.all()
    serializer_class = ProductoSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [EsAdministrador | EsTrabajadorDeTienda]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Producto.objects.none()

        # Admin/Superuser ve todo
        if user.is_superuser or user.tipo_usuario == 'ADMIN':
            return Producto.objects.all()

        # Trabajador ve solo productos de su tienda vinculada
        if user.tipo_usuario == 'TRABAJADOR':
            tiendas_ids = TrabajadorTienda.objects.filter(trabajador=user).values_list('tienda_id', flat=True)
            return Producto.objects.filter(tienda_id__in=tiendas_ids)

        # Cliente ve todos los productos
        return Producto.objects.all()

    def perform_create(self, serializer):
        user = self.request.user
        # Si es trabajador, forzar que la tienda del producto sea la que tiene vinculada
        if user.tipo_usuario == 'TRABAJADOR':
            tiendas_ids = list(TrabajadorTienda.objects.filter(trabajador=user).values_list('tienda_id', flat=True))
            tienda_solicitada = serializer.validated_data.get('tienda')
            
            if not tienda_solicitada or tienda_solicitada.id not in tiendas_ids:
                raise permissions.exceptions.PermissionDenied(
                    "No puedes crear productos para una tienda a la que no estás vinculado."
                )
        serializer.save()


class PedidoViewSet(viewsets.ModelViewSet):
    queryset = Pedido.objects.all()
    serializer_class = PedidoSerializer

    def get_permissions(self):
        if self.action == 'create':
            permission_classes = [permissions.IsAuthenticated] # Cualquier usuario autenticado puede comprar
        elif self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [EsAdministrador] # Solo admin modifica pedidos globalmente
        else:
            permission_classes = [EsAdministrador | EsTrabajadorDeTienda | EsClientePropietario]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Pedido.objects.none()

        # Administrador ve todos los pedidos
        if user.is_superuser or user.tipo_usuario == 'ADMIN':
            return Pedido.objects.all()

        # Trabajador ve pedidos de tiendas a las que está vinculado
        if user.tipo_usuario == 'TRABAJADOR':
            tiendas_ids = TrabajadorTienda.objects.filter(trabajador=user).values_list('tienda_id', flat=True)
            # Retorna pedidos que contienen al menos un producto de las tiendas del trabajador
            return Pedido.objects.filter(detalles__producto__tienda_id__in=tiendas_ids).distinct()

        # Cliente ve únicamente sus propios pedidos
        return Pedido.objects.filter(cliente=user)

    def perform_create(self, serializer):
        # Asegurar que el cliente del pedido sea el usuario autenticado
        serializer.save(cliente=self.request.user)


class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer

    def get_permissions(self):
        if self.action in ['create']:
            # Permitir registro público (clientes)
            return [permissions.AllowAny()]
        return [EsAdministrador()]


# Vistas de Prueba y Navegación del Frontend
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count

def home(request):
    tiendas = Tienda.objects.filter(estado_tienda='Activa').order_by('nombre_comercial')
    productos = Producto.objects.select_related('tienda', 'categoria').order_by('-id')
    categorias_destacadas = (
        Categoria.objects.filter(estado=True)
        .annotate(total_productos=Count('productos'))
        .filter(total_productos__gt=0)
        .order_by('-total_productos', 'nombre_categoria')[:6]
    )
    tiendas_por_ventas = tiendas.annotate(ventas=Count('productos__detallepedido')).order_by('-ventas', 'nombre_comercial')[:6]
    context = {
        'tiendas': tiendas,
        'productos': productos,
        'tiendas_count': tiendas.count(),
        'productos_count': productos.count(),
        'categorias_count': Categoria.objects.filter(estado=True).count(),
        'tiendas_destacadas': tiendas_por_ventas,
        'productos_destacados': productos[:8],
        'categorias_destacadas': categorias_destacadas,
    }
    return render(request, 'home.html', context)


@login_required
def test_dashboard(request):
    usuario = request.user
    
    if usuario.is_superuser or usuario.tipo_usuario == 'ADMIN':
        total_rev = Pedido.objects.aggregate(total=Sum('total'))['total'] or 0.0
        # Dar formato monetario simple
        total_revenue = f"{int(round(float(total_rev))):,}".replace(",", ".")
        
        total_stores = Tienda.objects.count()
        total_users = Usuario.objects.count()
        tiendas = Tienda.objects.all()
        
        context = {
            'usuario': usuario,
            'total_revenue': total_revenue,
            'total_stores': total_stores,
            'total_users': total_users,
            'tiendas': tiendas,
        }
        return render(request, 'dashboard_admin.html', context)
        
    elif usuario.tipo_usuario == 'TRABAJADOR':
        tiendas_ids = TrabajadorTienda.objects.filter(trabajador=usuario).values_list('tienda_id', flat=True)
        tiendas = Tienda.objects.filter(id__in=tiendas_ids)
        productos = Producto.objects.filter(tienda_id__in=tiendas_ids)
        pedidos = Pedido.objects.filter(detalles__producto__tienda_id__in=tiendas_ids).distinct()
        
        context = {
            'usuario': usuario,
            'tiendas': tiendas,
            'productos': productos,
            'pedidos': pedidos,
        }
        return render(request, 'dashboard_trabajador.html', context)
        
    else: # CLIENTE
        pedidos = Pedido.objects.filter(cliente=usuario)
        puntos = pedidos.count() * 120
        # Seleccionar algunos productos del catálogo general para recomendar
        productos_recomendados = Producto.objects.all()[:3]
        
        context = {
            'usuario': usuario,
            'pedidos': pedidos,
            'puntos': puntos,
            'productos_recomendados': productos_recomendados,
        }
        return render(request, 'dashboard_cliente.html', context)


# Vistas dinámicas adicionales
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth import login
from django.db import transaction
from django.core.exceptions import PermissionDenied
from .models import Municipio, Departamento, Direccion

def register_view(request):
    if request.user.is_authenticated:
        return redirect('test_dashboard')
        
    error = None
    categorias = Categoria.objects.filter(estado=True).order_by('nombre_categoria')
    if request.method == 'POST':
        tipo_usuario = request.POST.get('tipo_usuario', 'CLIENTE')
        store_name = request.POST.get('store_name', '').strip()
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        selected_categoria_ids = [int(cid) for cid in request.POST.getlist('categorias') if cid.isdigit()]
        
        if not name or not email or not password:
            error = "Todos los campos obligatorios deben ser completados."
        elif tipo_usuario == 'TRABAJADOR' and not store_name:
            error = "Debes ingresar un nombre para la tienda."
        elif tipo_usuario == 'TRABAJADOR' and not selected_categoria_ids:
            error = "Debes seleccionar al menos una categoría para tu tienda."
        elif Usuario.objects.filter(username=email).exists() or Usuario.objects.filter(email=email).exists():
            error = "El correo electrónico ya está registrado."
        else:
            try:
                with transaction.atomic():
                    name_parts = name.split(' ', 1)
                    first_name = name_parts[0]
                    last_name = name_parts[1] if len(name_parts) > 1 else ''
                    
                    user = Usuario.objects.create_user(
                        username=email,
                        email=email,
                        password=password,
                        first_name=first_name,
                        last_name=last_name,
                        tipo_usuario=tipo_usuario
                    )

                    if selected_categoria_ids:
                        user.categorias_interes.set(Categoria.objects.filter(id__in=selected_categoria_ids))
                    
                    if tipo_usuario == 'TRABAJADOR':
                        tienda = Tienda.objects.create(
                            nombre_comercial=store_name,
                            razon_social=store_name,
                            correo_atencion=email,
                            telefono_atencion='',
                            estado_tienda='Activa'
                        )
                        tienda.categorias.set(Categoria.objects.filter(id__in=selected_categoria_ids))
                        TrabajadorTienda.objects.create(
                            tienda=tienda,
                            trabajador=user
                        )
                        
                    login(request, user)
                    return redirect('test_dashboard')
            except Exception as e:
                error = f"Error al registrar el usuario: {str(e)}"
                
    return render(request, 'registro.html', {'error': error, 'categorias': categorias})


def producto_detalle_view(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    return render(request, 'producto_detalle.html', {'producto': producto})


@login_required
def perfil_settings_view(request):
    usuario = request.user
    success = False
    if request.method == 'POST':
        usuario.first_name = request.POST.get('first_name', '').strip()
        usuario.last_name = request.POST.get('last_name', '').strip()
        usuario.email = request.POST.get('email', '').strip()
        usuario.telefono = request.POST.get('telefono', '').strip()
        
        nomenclatura = request.POST.get('nomenclatura', '').strip()
        barrio = request.POST.get('barrio', '').strip()
        codigo_postal = request.POST.get('codigo_postal', '').strip()
        municipio_id = request.POST.get('municipio_id', '')
        
        if nomenclatura or barrio or codigo_postal or municipio_id:
            municipio = None
            if municipio_id:
                municipio = Municipio.objects.filter(id=municipio_id).first()
            if not municipio:
                municipio = Municipio.objects.first()
            if not municipio:
                depto, _ = Departamento.objects.get_or_create(nombre="Antioquia", codigo_dane="05")
                municipio, _ = Municipio.objects.get_or_create(departamento=depto, nombre="Medellín", codigo_dane="05001")
                
            if usuario.direccion_principal:
                dir_obj = usuario.direccion_principal
                dir_obj.nomenclatura = nomenclatura
                dir_obj.barrio = barrio
                dir_obj.codigo_postal = codigo_postal
                dir_obj.municipio = municipio
                dir_obj.save()
            else:
                dir_obj = Direccion.objects.create(
                    nomenclatura=nomenclatura,
                    barrio=barrio,
                    codigo_postal=codigo_postal,
                    municipio=municipio
                )
                usuario.direccion_principal = dir_obj
                
        usuario.save()
        success = True
        
    departamentos = Departamento.objects.all()
    municipios = Municipio.objects.all()
    
    return render(request, 'perfil_settings.html', {
        'user': usuario, 
        'success': success,
        'departamentos': departamentos,
        'municipios': municipios
    })


def tienda_publico_view(request, pk):
    tienda = get_object_or_404(Tienda, pk=pk)
    productos = Producto.objects.filter(tienda=tienda)
    return render(request, 'tienda_publico.html', {'tienda': tienda, 'productos': productos})


@login_required
def inventario_trabajador_view(request):
    usuario = request.user
    if usuario.tipo_usuario != 'TRABAJADOR' and not usuario.is_superuser:
        raise PermissionDenied("Solo los trabajadores pueden gestionar el inventario.")
        
    tiendas_ids = TrabajadorTienda.objects.filter(trabajador=usuario).values_list('tienda_id', flat=True)
    productos = Producto.objects.filter(tienda_id__in=tiendas_ids)
    
    total_products = productos.count()
    active_listings = productos.count()
    low_stock_items = productos.filter(cantidad_stock__gt=0, cantidad_stock__lte=5).count()
    out_of_stock = productos.filter(cantidad_stock=0).count()
    
    context = {
        'productos': productos,
        'total_products': total_products,
        'active_listings': active_listings,
        'low_stock_items': low_stock_items,
        'out_of_stock': out_of_stock,
        'tiendas': Tienda.objects.filter(id__in=tiendas_ids),
    }
    return render(request, 'inventario_trabajador.html', context)


@login_required
def historial_pedidos_view(request):
    usuario = request.user
    
    if usuario.tipo_usuario == 'TRABAJADOR' or usuario.is_superuser:
        tiendas_ids = TrabajadorTienda.objects.filter(trabajador=usuario).values_list('tienda_id', flat=True)
        pedidos = Pedido.objects.filter(detalles__producto__tienda_id__in=tiendas_ids).distinct()
        is_worker = True
    else:
        pedidos = Pedido.objects.filter(cliente=usuario)
        is_worker = False
        
    return render(request, 'historial_pedidos.html', {
        'pedidos': pedidos,
        'is_worker': is_worker
    })


# --- Nuevas Vistas del Scope: CRUD de Inventario, Detalle de Pedidos y Paneles de Administración ---

@login_required
def producto_crear_view(request):
    usuario = request.user
    if usuario.tipo_usuario != 'TRABAJADOR' and not usuario.is_superuser:
        raise PermissionDenied("Solo los trabajadores de tienda pueden crear productos.")
    
    trabajador_tienda = TrabajadorTienda.objects.filter(trabajador=usuario).first()
    if not trabajador_tienda and not usuario.is_superuser:
        raise PermissionDenied("No estás vinculado a ninguna tienda.")
        
    tienda = trabajador_tienda.tienda if trabajador_tienda else Tienda.objects.first()
    
    error = None
    if request.method == 'POST':
        descripcion_corta = request.POST.get('descripcion_corta', '').strip()
        categoria_id = request.POST.get('categoria', '')
        marca = request.POST.get('marca', '').strip()
        descripcion_larga = request.POST.get('descripcion_larga', '').strip()
        precio_unitario = request.POST.get('precio_unitario', '')
        cantidad_stock = request.POST.get('cantidad_stock', '0')
        imagen_principal = request.FILES.get('url_imagen_principal')
        
        if not descripcion_corta or not categoria_id or not precio_unitario:
            error = "El título, la categoría y el precio son obligatorios."
        else:
            try:
                categoria = Categoria.objects.get(id=categoria_id)
                precio_unitario_decimal = float(precio_unitario)
                cantidad_stock_int = int(cantidad_stock)
                
                Producto.objects.create(
                    tienda=tienda,
                    descripcion_corta=descripcion_corta,
                    descripcion_larga=descripcion_larga,
                    url_imagen_principal=_save_uploaded_media(imagen_principal, 'productos') or "https://images.unsplash.com/photo-1523275335684-37898b6baf30",
                    categoria=categoria,
                    especificaciones={"marca": marca} if marca else {},
                    precio_unitario=precio_unitario_decimal,
                    cantidad_stock=cantidad_stock_int
                )
                return redirect('inventario_trabajador')
            except Exception as e:
                error = f"Error al crear el producto: {str(e)}"
                
    categorias = Categoria.objects.filter(estado=True)
    return render(request, 'producto_crear_editar.html', {
        'categorias': categorias,
        'tienda': tienda,
        'error': error
    })


@login_required
def producto_editar_view(request, pk):
    usuario = request.user
    producto = get_object_or_404(Producto, pk=pk)
    
    if not usuario.is_superuser:
        if usuario.tipo_usuario != 'TRABAJADOR':
            raise PermissionDenied("Solo los trabajadores de tienda pueden editar productos.")
        if not TrabajadorTienda.objects.filter(trabajador=usuario, tienda=producto.tienda).exists():
            raise PermissionDenied("No tienes permisos para editar productos de esta tienda.")
            
    error = None
    if request.method == 'POST':
        descripcion_corta = request.POST.get('descripcion_corta', '').strip()
        categoria_id = request.POST.get('categoria', '')
        marca = request.POST.get('marca', '').strip()
        descripcion_larga = request.POST.get('descripcion_larga', '').strip()
        precio_unitario = request.POST.get('precio_unitario', '')
        cantidad_stock = request.POST.get('cantidad_stock', '0')
        imagen_principal = request.FILES.get('url_imagen_principal')
        
        if not descripcion_corta or not categoria_id or not precio_unitario:
            error = "El título, la categoría y el precio son obligatorios."
        else:
            try:
                categoria = Categoria.objects.get(id=categoria_id)
                producto.descripcion_corta = descripcion_corta
                producto.descripcion_larga = descripcion_larga
                nueva_imagen = _save_uploaded_media(imagen_principal, 'productos')
                if nueva_imagen:
                    producto.url_imagen_principal = nueva_imagen
                producto.categoria = categoria
                producto.especificaciones = {"marca": marca} if marca else {}
                producto.precio_unitario = float(precio_unitario)
                producto.cantidad_stock = int(cantidad_stock)
                producto.save()
                return redirect('inventario_trabajador')
            except Exception as e:
                error = f"Error al actualizar el producto: {str(e)}"
                
    categorias = Categoria.objects.filter(estado=True)
    precio_decimal = str(producto.precio_unitario).replace(',', '.')
    return render(request, 'producto_crear_editar.html', {
        'producto': producto,
        'categorias': categorias,
        'tienda': producto.tienda,
        'precio_decimal': precio_decimal,
        'error': error
    })


@login_required
def producto_eliminar_view(request, pk):
    if request.method != 'POST':
        return redirect('inventario_trabajador')
        
    usuario = request.user
    producto = get_object_or_404(Producto, pk=pk)
    
    if not usuario.is_superuser:
        if usuario.tipo_usuario != 'TRABAJADOR':
            raise PermissionDenied("Solo los trabajadores de tienda pueden eliminar productos.")
        if not TrabajadorTienda.objects.filter(trabajador=usuario, tienda=producto.tienda).exists():
            raise PermissionDenied("No tienes permisos para eliminar productos de esta tienda.")
            
    producto.delete()
    return redirect('inventario_trabajador')


@login_required
def pedido_detalle_trabajador_view(request, pk):
    usuario = request.user
    pedido = get_object_or_404(Pedido, pk=pk)
    
    if not usuario.is_superuser:
        if usuario.tipo_usuario != 'TRABAJADOR':
            raise PermissionDenied("Acceso restringido a trabajadores.")
        
        tiendas_ids = TrabajadorTienda.objects.filter(trabajador=usuario).values_list('tienda_id', flat=True)
        if not pedido.detalles.filter(producto__tienda_id__in=tiendas_ids).exists():
            raise PermissionDenied("No tienes permisos para ver este pedido.")
            
    success = False
    if request.method == 'POST':
        estado_id = request.POST.get('estado_id', '')
        if estado_id:
            estado = get_object_or_404(EstadoPedido, id=estado_id)
            pedido.estado_pedido = estado
            pedido.save()
            success = True
            
    if usuario.is_superuser:
        detalles = pedido.detalles.all()
    else:
        tiendas_ids = TrabajadorTienda.objects.filter(trabajador=usuario).values_list('tienda_id', flat=True)
        detalles = pedido.detalles.filter(producto__tienda_id__in=tiendas_ids)
        
    estados = EstadoPedido.objects.all()
    return render(request, 'pedido_detalle_trabajador.html', {
        'pedido': pedido,
        'detalles': detalles,
        'estados': estados,
        'success': success
    })


@login_required
def pedido_detalle_cliente_view(request, pk):
    usuario = request.user
    pedido = get_object_or_404(Pedido, pk=pk)
    
    if not usuario.is_superuser and usuario.tipo_usuario != 'ADMIN':
        if pedido.cliente != usuario:
            raise PermissionDenied("No tienes permisos para ver este pedido.")
            
    detalles = pedido.detalles.all()
    return render(request, 'pedido_detalle_cliente.html', {
        'pedido': pedido,
        'detalles': detalles
    })


@login_required
def admin_tiendas_view(request):
    usuario = request.user
    if usuario.tipo_usuario != 'ADMIN' and not usuario.is_superuser:
        raise PermissionDenied("Solo los administradores pueden ver este panel.")
        
    if request.method == 'POST':
        tienda_id = request.POST.get('tienda_id', '')
        action = request.POST.get('action', '')
        if tienda_id and action:
            tienda = get_object_or_404(Tienda, id=tienda_id)
            if action == 'suspend':
                tienda.estado_tienda = 'Suspendida'
            elif action == 'activate':
                tienda.estado_tienda = 'Activa'
            tienda.save()
            return redirect('admin_tiendas')
            
    tiendas = Tienda.objects.all()
    tienda_records = []
    
    for t in tiendas:
        revenue = t.productos.filter(detallepedido__pedido__isnull=False).aggregate(sum=Sum('detallepedido__subtotal'))['sum'] or 0.0
        trabajador_obj = TrabajadorTienda.objects.filter(tienda=t).first()
        trabajador = trabajador_obj.trabajador if trabajador_obj else None
        
        tienda_records.append({
            'tienda': t,
            'revenue': f"{int(round(float(revenue))):,}".replace(",", "."),
            'trabajador': trabajador
        })
        
    return render(request, 'admin_tiendas.html', {
        'tienda_records': tienda_records
    })


@login_required
def admin_usuarios_view(request):
    usuario = request.user
    if usuario.tipo_usuario != 'ADMIN' and not usuario.is_superuser:
        raise PermissionDenied("Solo los administradores pueden ver este panel.")
        
    if request.method == 'POST':
        user_to_toggle_id = request.POST.get('user_to_toggle_id', '')
        action = request.POST.get('action', '')
        if user_to_toggle_id and action:
            user_to_toggle = get_object_or_404(Usuario, id=user_to_toggle_id)
            if user_to_toggle.id != usuario.id:
                if action == 'suspend':
                    user_to_toggle.is_active = False
                elif action == 'activate':
                    user_to_toggle.is_active = True
                user_to_toggle.save()
            return redirect('admin_usuarios')
            
    usuarios_list = Usuario.objects.all().order_by('id')
    return render(request, 'admin_usuarios.html', {
        'usuarios_list': usuarios_list
    })


def catalogo_search_view(request):
    query = request.GET.get('q', '').strip()
    selected_categorias = request.GET.getlist('category_id')
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')
    
    productos = Producto.objects.all()
    
    if query:
        productos = productos.filter(descripcion_corta__icontains=query) | productos.filter(descripcion_larga__icontains=query)
        
    if selected_categorias:
        selected_categorias_ints = [int(cid) for cid in selected_categorias if cid.isdigit()]
        if selected_categorias_ints:
            productos = productos.filter(categoria_id__in=selected_categorias_ints)
            
    if min_price:
        try:
            productos = productos.filter(precio_unitario__gte=float(min_price))
        except ValueError:
            pass
            
    if max_price:
        try:
            productos = productos.filter(precio_unitario__lte=float(max_price))
        except ValueError:
            pass
            
    categorias = Categoria.objects.filter(estado=True)
    selected_categorias_ints = [int(cid) for cid in selected_categorias if cid.isdigit()]
    
    return render(request, 'catalogo.html', {
        'productos': productos,
        'categorias': categorias,
        'selected_categorias': selected_categorias_ints,
        'query': query,
        'min_price': min_price,
        'max_price': max_price
    })


# ViewSets de API REST adicionales para Departamento, Municipio y Direccion
from .serializers import DepartamentoSerializer, MunicipioSerializer, DireccionSerializer

class DepartamentoViewSet(viewsets.ModelViewSet):
    queryset = Departamento.objects.all()
    serializer_class = DepartamentoSerializer
    permission_classes = [permissions.IsAuthenticated]

class MunicipioViewSet(viewsets.ModelViewSet):
    queryset = Municipio.objects.all()
    serializer_class = MunicipioSerializer
    permission_classes = [permissions.IsAuthenticated]

class DireccionViewSet(viewsets.ModelViewSet):
    queryset = Direccion.objects.all()
    serializer_class = DireccionSerializer
    permission_classes = [permissions.IsAuthenticated]


# --- Nuevas Vistas de Carrito de Compras y Checkout ---

@login_required
def agregar_al_carrito_view(request, producto_id):
    if request.user.tipo_usuario != 'CLIENTE':
        return redirect('home')
    producto = get_object_or_404(Producto, id=producto_id)
    cantidad = int(request.POST.get('cantidad', 1))
    
    # Obtener o crear carrito activo del cliente
    carrito, _ = Carrito.objects.get_or_create(cliente=request.user, estado='Activo')
    
    # Validar stock disponible
    if cantidad > producto.cantidad_stock:
        cantidad = producto.cantidad_stock
        
    if cantidad <= 0:
        return redirect('producto_detalle', pk=producto.id)
        
    item, created = ItemCarrito.objects.get_or_create(carrito=carrito, producto=producto)
    if not created:
        nueva_cantidad = item.cantidad + cantidad
        if nueva_cantidad > producto.cantidad_stock:
            nueva_cantidad = producto.cantidad_stock
        item.cantidad = nueva_cantidad
    else:
        item.cantidad = cantidad
    item.save()
    
    return redirect('carrito_detalle')


@login_required
def carrito_detalle_view(request):
    if request.user.tipo_usuario != 'CLIENTE':
        return redirect('home')
    carrito, _ = Carrito.objects.get_or_create(cliente=request.user, estado='Activo')
    items = carrito.items.all().select_related('producto', 'producto__tienda')
    
    # Calcular totales
    subtotal = sum(item.get_item_price for item in items)
    costo_envio = 10000.0 if items.exists() else 0.0  # Costo de envío fijo
    total = subtotal + costo_envio
    
    return render(request, 'carrito_detalle.html', {
        'carrito': carrito,
        'items': items,
        'subtotal': subtotal,
        'costo_envio': costo_envio,
        'total': total,
    })


@login_required
def remover_del_carrito_view(request, item_id):
    if request.user.tipo_usuario != 'CLIENTE':
        return redirect('home')
    item = get_object_or_404(ItemCarrito, id=item_id, carrito__cliente=request.user, carrito__estado='Activo')
    item.delete()
    return redirect('carrito_detalle')


@login_required
def actualizar_item_carrito_view(request, item_id):
    if request.user.tipo_usuario != 'CLIENTE':
        return redirect('home')
    item = get_object_or_404(ItemCarrito, id=item_id, carrito__cliente=request.user, carrito__estado='Activo')
    
    if request.method == 'POST':
        accion = request.POST.get('accion')
        if accion == 'incrementar':
            if item.cantidad < item.producto.cantidad_stock:
                item.cantidad += 1
                item.save()
        elif accion == 'decrementar':
            if item.cantidad > 1:
                item.cantidad -= 1
                item.save()
            else:
                item.delete()
    return redirect('carrito_detalle')


@login_required
def realizar_pedido_view(request):
    if request.user.tipo_usuario != 'CLIENTE':
        return redirect('home')
        
    carrito, _ = Carrito.objects.get_or_create(cliente=request.user, estado='Activo')
    items = carrito.items.all().select_related('producto')
    
    if not items.exists():
        return redirect('carrito_detalle')
        
    subtotal = sum(item.get_item_price for item in items)
    costo_envio = 10000.0
    total = subtotal + costo_envio
    
    error = None
    if request.method == 'POST':
        direccion_id = request.POST.get('direccion_id')
        
        # Opciones de dirección
        direccion_cliente = None
        if direccion_id == 'nueva':
            nomenclatura = request.POST.get('nomenclatura', '').strip()
            barrio = request.POST.get('barrio', '').strip()
            municipio_id = request.POST.get('municipio_id', '')
            etiqueta = request.POST.get('etiqueta', 'Casa').strip()
            nombre_recibidor = request.POST.get('nombre_recibidor', '').strip()
            telefono_recibidor = request.POST.get('telefono_recibidor', '').strip()
            
            if not nomenclatura or not barrio or not municipio_id or not nombre_recibidor or not telefono_recibidor:
                error = "Todos los campos de la nueva dirección son obligatorios."
            else:
                municipio = get_object_or_404(Municipio, id=municipio_id)
                direccion = Direccion.objects.create(
                    nomenclatura=nomenclatura,
                    barrio=barrio,
                    municipio=municipio
                )
                direccion_cliente = DireccionCliente.objects.create(
                    cliente=request.user,
                    direccion=direccion,
                    etiqueta=etiqueta,
                    nombre_recibidor=nombre_recibidor,
                    telefono_recibidor=telefono_recibidor
                )
        else:
            direccion_cliente = DireccionCliente.objects.filter(id=direccion_id, cliente=request.user).first()
            if not direccion_cliente:
                error = "Debe seleccionar o registrar una dirección de envío."
                
        if not error:
            # Validar stock para todos los productos antes de crear el pedido
            stock_ok = True
            for item in items:
                if item.cantidad > item.producto.cantidad_stock:
                    stock_ok = False
                    error = f"El producto {item.producto.descripcion_corta} no tiene suficiente stock disponible."
                    break
            
            if stock_ok:
                try:
                    with transaction.atomic():
                        # Generar comprobante único
                        import uuid
                        comprobante = f"MS-{uuid.uuid4().hex[:8].upper()}"
                        
                        estado_inicial = EstadoPedido.objects.filter(nombre_estado="Creado").first()
                        if not estado_inicial:
                            estado_inicial = EstadoPedido.objects.create(nombre_estado="Creado")
                            
                        # Crear el pedido
                        pedido = Pedido.objects.create(
                            cliente=request.user,
                            direccion_cliente=direccion_cliente,
                            numero_comprobante=comprobante,
                            subtotal=subtotal,
                            costo_envio=costo_envio,
                            total=total,
                            estado_pedido=estado_inicial
                        )
                        
                        # Crear detalles del pedido y restar stock
                        for item in items:
                            DetallePedido.objects.create(
                                pedido=pedido,
                                producto=item.producto,
                                nombre_producto=item.producto.descripcion_corta,
                                precio_compra=item.producto.precio_unitario,
                                cantidad=item.cantidad,
                                subtotal=item.get_item_price
                            )
                            # Restar stock
                            producto = item.producto
                            producto.cantidad_stock -= item.cantidad
                            producto.save()
                            
                        # Cambiar estado del carrito
                        carrito.estado = 'Convertido'
                        carrito.save()
                        
                        return redirect('pedido_exitoso', pk=pedido.id)
                except Exception as e:
                    error = f"Error al procesar el pedido: {str(e)}"
                    
    direcciones = DireccionCliente.objects.filter(cliente=request.user).select_related('direccion', 'direccion__municipio', 'direccion__municipio__departamento')
    departamentos = Departamento.objects.all()
    municipios = Municipio.objects.all()
    
    return render(request, 'realizar_pedido.html', {
        'items': items,
        'subtotal': subtotal,
        'costo_envio': costo_envio,
        'total': total,
        'direcciones': direcciones,
        'departamentos': departamentos,
        'municipios': municipios,
        'error': error
    })


@login_required
def pedido_exitoso_view(request, pk):
    if request.user.tipo_usuario != 'CLIENTE':
        return redirect('home')
    pedido = get_object_or_404(Pedido, id=pk, cliente=request.user)
    return render(request, 'pedido_exitoso.html', {'pedido': pedido})


# --- CRUD de Administración para Clientes, Empleados, Tiendas y Pedidos ---

def check_admin_user(user):
    if not (user.is_authenticated and (user.tipo_usuario == 'ADMIN' or user.is_superuser)):
        raise PermissionDenied("Solo los administradores pueden realizar esta acción.")

@login_required
def admin_usuario_crear_view(request):
    check_admin_user(request.user)
    error = None
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        email = request.POST.get('email', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        tipo_usuario = request.POST.get('tipo_usuario', 'CLIENTE')
        documento = request.POST.get('documento', '').strip()
        telefono = request.POST.get('telefono', '').strip()
        tienda_id = request.POST.get('tienda_id', '')

        if not username or not password or not email:
            error = "El nombre de usuario, contraseña y correo son obligatorios."
        elif Usuario.objects.filter(username=username).exists():
            error = "El nombre de usuario ya existe."
        elif Usuario.objects.filter(email=email).exists():
            error = "El correo electrónico ya está registrado."
        else:
            try:
                usuario_nuevo = Usuario.objects.create_user(
                    username=username,
                    password=password,
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                    tipo_usuario=tipo_usuario,
                    documento=documento,
                    telefono=telefono
                )
                if tipo_usuario == 'TRABAJADOR' and tienda_id:
                    tienda = Tienda.objects.get(id=tienda_id)
                    TrabajadorTienda.objects.create(trabajador=usuario_nuevo, tienda=tienda)
                return redirect('admin_usuarios')
            except Exception as e:
                error = f"Error al crear el usuario: {str(e)}"

    tiendas = Tienda.objects.all()
    return render(request, 'admin_usuario_form.html', {
        'tiendas': tiendas,
        'tipo_usuario_choices': Usuario.TIPO_USUARIO_CHOICES,
        'error': error
    })

@login_required
def admin_usuario_editar_view(request, pk):
    check_admin_user(request.user)
    usuario_edit = get_object_or_404(Usuario, pk=pk)
    error = None
    
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        email = request.POST.get('email', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        tipo_usuario = request.POST.get('tipo_usuario', 'CLIENTE')
        documento = request.POST.get('documento', '').strip()
        telefono = request.POST.get('telefono', '').strip()
        tienda_id = request.POST.get('tienda_id', '')
        is_active = request.POST.get('is_active', '') == 'on'

        if not username or not email:
            error = "El nombre de usuario y correo son obligatorios."
        elif Usuario.objects.filter(username=username).exclude(pk=pk).exists():
            error = "El nombre de usuario ya está en uso por otra cuenta."
        elif Usuario.objects.filter(email=email).exclude(pk=pk).exists():
            error = "El correo electrónico ya está en uso por otra cuenta."
        else:
            try:
                usuario_edit.username = username
                usuario_edit.email = email
                usuario_edit.first_name = first_name
                usuario_edit.last_name = last_name
                usuario_edit.tipo_usuario = tipo_usuario
                usuario_edit.documento = documento
                usuario_edit.telefono = telefono
                usuario_edit.is_active = is_active
                
                if password:
                    usuario_edit.set_password(password)
                
                usuario_edit.save()

                # Limpiar cualquier relación previa si ya no es trabajador
                TrabajadorTienda.objects.filter(trabajador=usuario_edit).delete()
                if tipo_usuario == 'TRABAJADOR' and tienda_id:
                    tienda = Tienda.objects.get(id=tienda_id)
                    TrabajadorTienda.objects.create(trabajador=usuario_edit, tienda=tienda)

                return redirect('admin_usuarios')
            except Exception as e:
                error = f"Error al actualizar el usuario: {str(e)}"

    tiendas = Tienda.objects.all()
    tienda_asignada = TrabajadorTienda.objects.filter(trabajador=usuario_edit).first()
    return render(request, 'admin_usuario_form.html', {
        'usuario_edit': usuario_edit,
        'tiendas': tiendas,
        'tienda_asignada': tienda_asignada.tienda if tienda_asignada else None,
        'tipo_usuario_choices': Usuario.TIPO_USUARIO_CHOICES,
        'error': error
    })

@login_required
def admin_usuario_eliminar_view(request, pk):
    check_admin_user(request.user)
    usuario_del = get_object_or_404(Usuario, pk=pk)
    if usuario_del.id == request.user.id:
        raise PermissionDenied("No puedes eliminar tu propio usuario administrador.")
    
    if request.method == 'POST':
        usuario_del.delete()
    return redirect('admin_usuarios')

@login_required
def admin_tienda_crear_view(request):
    check_admin_user(request.user)
    error = None
    if request.method == 'POST':
        nombre_comercial = request.POST.get('nombre_comercial', '').strip()
        descripcion = request.POST.get('descripcion', '').strip()
        logo_file = request.FILES.get('url_logo')
        correo_atencion = request.POST.get('correo_atencion', '').strip()
        telefono_atencion = request.POST.get('telefono_atencion', '').strip()
        razon_social = request.POST.get('razon_social', '').strip()
        estado_tienda = request.POST.get('estado_tienda', 'Activa')
        plan_id = request.POST.get('plan_id', '')
        fecha_vencimiento = request.POST.get('fecha_vencimiento_suscripcion', '')
        trabajador_id = request.POST.get('trabajador_id', '')

        if not nombre_comercial or not correo_atencion or not razon_social:
            error = "El nombre comercial, correo de atención y razón social son obligatorios."
        else:
            try:
                from django.utils.dateparse import parse_datetime
                plan_id_val = int(plan_id) if plan_id.isdigit() else None
                fecha_venc_val = parse_datetime(fecha_vencimiento) if fecha_vencimiento else None

                tienda = Tienda.objects.create(
                    nombre_comercial=nombre_comercial,
                    descripcion=descripcion,
                    url_logo=_save_uploaded_media(logo_file, 'tiendas') or "https://images.unsplash.com/photo-1578916171728-46686eac8d58",
                    correo_atencion=correo_atencion,
                    telefono_atencion=telefono_atencion,
                    razon_social=razon_social,
                    estado_tienda=estado_tienda,
                    plan_id=plan_id_val,
                    fecha_vencimiento_suscripcion=fecha_venc_val
                )

                if trabajador_id:
                    worker = Usuario.objects.get(id=trabajador_id)
                    TrabajadorTienda.objects.create(tienda=tienda, trabajador=worker)

                return redirect('admin_tiendas')
            except Exception as e:
                error = f"Error al crear la tienda: {str(e)}"

    trabajadores = Usuario.objects.filter(tipo_usuario='TRABAJADOR')
    return render(request, 'admin_tienda_form.html', {
        'trabajadores': trabajadores,
        'error': error
    })

@login_required
def admin_tienda_editar_view(request, pk):
    check_admin_user(request.user)
    tienda = get_object_or_404(Tienda, pk=pk)
    error = None

    if request.method == 'POST':
        nombre_comercial = request.POST.get('nombre_comercial', '').strip()
        descripcion = request.POST.get('descripcion', '').strip()
        logo_file = request.FILES.get('url_logo')
        correo_atencion = request.POST.get('correo_atencion', '').strip()
        telefono_atencion = request.POST.get('telefono_atencion', '').strip()
        razon_social = request.POST.get('razon_social', '').strip()
        estado_tienda = request.POST.get('estado_tienda', 'Activa')
        plan_id = request.POST.get('plan_id', '')
        fecha_vencimiento = request.POST.get('fecha_vencimiento_suscripcion', '')
        trabajador_id = request.POST.get('trabajador_id', '')

        if not nombre_comercial or not correo_atencion or not razon_social:
            error = "El nombre comercial, correo de atención y razón social son obligatorios."
        else:
            try:
                from django.utils.dateparse import parse_datetime
                plan_id_val = int(plan_id) if plan_id.isdigit() else None
                fecha_venc_val = parse_datetime(fecha_vencimiento) if fecha_vencimiento else None

                tienda.nombre_comercial = nombre_comercial
                tienda.descripcion = descripcion
                nueva_logo = _save_uploaded_media(logo_file, 'tiendas')
                if nueva_logo:
                    tienda.url_logo = nueva_logo
                tienda.correo_atencion = correo_atencion
                tienda.telefono_atencion = telefono_atencion
                tienda.razon_social = razon_social
                tienda.estado_tienda = estado_tienda
                tienda.plan_id = plan_id_val
                tienda.fecha_vencimiento_suscripcion = fecha_venc_val
                tienda.save()

                # Limpiar encargado anterior y asociar nuevo
                TrabajadorTienda.objects.filter(tienda=tienda).delete()
                if trabajador_id:
                    worker = Usuario.objects.get(id=trabajador_id)
                    TrabajadorTienda.objects.create(tienda=tienda, trabajador=worker)

                return redirect('admin_tiendas')
            except Exception as e:
                error = f"Error al actualizar la tienda: {str(e)}"

    trabajadores = Usuario.objects.filter(tipo_usuario='TRABAJADOR')
    trabajador_actual = TrabajadorTienda.objects.filter(tienda=tienda).first()
    return render(request, 'admin_tienda_form.html', {
        'tienda': tienda,
        'trabajadores': trabajadores,
        'trabajador_actual': trabajador_actual.trabajador if trabajador_actual else None,
        'error': error
    })

@login_required
def admin_tienda_eliminar_view(request, pk):
    check_admin_user(request.user)
    tienda = get_object_or_404(Tienda, pk=pk)
    if request.method == 'POST':
        tienda.delete()
    return redirect('admin_tiendas')

@login_required
def admin_pedidos_view(request):
    check_admin_user(request.user)
    estado_filtro = request.GET.get('estado', '')
    pedidos = Pedido.objects.all().order_by('-fecha_actualizacion')
    
    if estado_filtro:
        pedidos = pedidos.filter(estado_pedido_id=estado_filtro)

    estados = EstadoPedido.objects.all()
    return render(request, 'admin_pedidos.html', {
        'pedidos': pedidos,
        'estados': estados,
        'estado_filtro': estado_filtro
    })

@login_required
def admin_pedido_crear_view(request):
    check_admin_user(request.user)
    error = None
    if request.method == 'POST':
        cliente_id = request.POST.get('cliente_id', '')
        estado_pedido_id = request.POST.get('estado_pedido_id', '')
        subtotal = request.POST.get('subtotal', '0')
        costo_envio = request.POST.get('costo_envio', '0')
        total = request.POST.get('total', '0')
        
        # Dirección
        nombre_recibidor = request.POST.get('nombre_recibidor', '').strip()
        telefono_recibidor = request.POST.get('telefono_recibidor', '').strip()
        nomenclatura = request.POST.get('nomenclatura', '').strip()
        barrio = request.POST.get('barrio', '').strip()
        municipio_id = request.POST.get('municipio_id', '')

        # Producto
        producto_id = request.POST.get('producto_id', '')
        cantidad = request.POST.get('cantidad', '1')

        if not cliente_id or not estado_pedido_id:
            error = "El cliente y el estado del pedido son obligatorios."
        else:
            try:
                import uuid
                from decimal import Decimal
                
                cliente = Usuario.objects.get(id=cliente_id)
                estado = EstadoPedido.objects.get(id=estado_pedido_id)
                
                # Crear dirección si se ingresaron datos
                dir_cliente_obj = None
                if nomenclatura and barrio and municipio_id:
                    municipio = Municipio.objects.get(id=municipio_id)
                    direccion_base = Direccion.objects.create(
                        nomenclatura=nomenclatura,
                        barrio=barrio,
                        municipio=municipio
                    )
                    dir_cliente_obj = DireccionCliente.objects.create(
                        cliente=cliente,
                        direccion=direccion_base,
                        etiqueta="Admin Registrado",
                        nombre_recibidor=nombre_recibidor or cliente.get_full_name() or cliente.username,
                        telefono_recibidor=telefono_recibidor or cliente.telefono or "0000000"
                    )

                numero_comprobante = "MS-ADM-" + str(uuid.uuid4())[:8].upper()

                pedido = Pedido.objects.create(
                    cliente=cliente,
                    direccion_cliente=dir_cliente_obj,
                    numero_comprobante=numero_comprobante,
                    subtotal=Decimal(subtotal),
                    costo_envio=Decimal(costo_envio),
                    total=Decimal(total),
                    estado_pedido=estado
                )

                if producto_id:
                    producto = Producto.objects.get(id=producto_id)
                    cant_val = int(cantidad)
                    subtotal_item = producto.precio_unitario * cant_val
                    
                    DetallePedido.objects.create(
                        pedido=pedido,
                        producto=producto,
                        nombre_producto=producto.descripcion_corta,
                        precio_compra=producto.precio_unitario,
                        cantidad=cant_val,
                        subtotal=subtotal_item
                    )
                    
                    # Opcional: descontar stock
                    producto.cantidad_stock = max(0, producto.cantidad_stock - cant_val)
                    producto.save()

                return redirect('admin_pedidos')
            except Exception as e:
                error = f"Error al crear el pedido: {str(e)}"

    clientes = Usuario.objects.filter(tipo_usuario='CLIENTE')
    estados = EstadoPedido.objects.all()
    productos = Producto.objects.filter(cantidad_stock__gt=0)
    municipios = Municipio.objects.all().select_related('departamento')

    return render(request, 'admin_pedido_form.html', {
        'clientes': clientes,
        'estados': estados,
        'productos': productos,
        'municipios': municipios,
        'error': error
    })

@login_required
def admin_pedido_editar_view(request, pk):
    check_admin_user(request.user)
    pedido = get_object_or_404(Pedido, pk=pk)
    error = None

    if request.method == 'POST':
        cliente_id = request.POST.get('cliente_id', '')
        estado_pedido_id = request.POST.get('estado_pedido_id', '')
        subtotal = request.POST.get('subtotal', '0')
        costo_envio = request.POST.get('costo_envio', '0')
        total = request.POST.get('total', '0')
        
        # Dirección
        nombre_recibidor = request.POST.get('nombre_recibidor', '').strip()
        telefono_recibidor = request.POST.get('telefono_recibidor', '').strip()
        nomenclatura = request.POST.get('nomenclatura', '').strip()
        barrio = request.POST.get('barrio', '').strip()
        municipio_id = request.POST.get('municipio_id', '')

        if not cliente_id or not estado_pedido_id:
            error = "El cliente y el estado del pedido son obligatorios."
        else:
            try:
                from decimal import Decimal
                cliente = Usuario.objects.get(id=cliente_id)
                estado = EstadoPedido.objects.get(id=estado_pedido_id)

                pedido.cliente = cliente
                pedido.estado_pedido = estado
                pedido.subtotal = Decimal(subtotal)
                pedido.costo_envio = Decimal(costo_envio)
                pedido.total = Decimal(total)

                # Actualizar o crear dirección
                if nomenclatura and barrio and municipio_id:
                    municipio = Municipio.objects.get(id=municipio_id)
                    if pedido.direccion_cliente:
                        dir_base = pedido.direccion_cliente.direccion
                        dir_base.nomenclatura = nomenclatura
                        dir_base.barrio = barrio
                        dir_base.municipio = municipio
                        dir_base.save()
                        
                        dir_cli = pedido.direccion_cliente
                        dir_cli.nombre_recibidor = nombre_recibidor
                        dir_cli.telefono_recibidor = telefono_recibidor
                        dir_cli.save()
                    else:
                        dir_base = Direccion.objects.create(
                            nomenclatura=nomenclatura,
                            barrio=barrio,
                            municipio=municipio
                        )
                        dir_cliente_obj = DireccionCliente.objects.create(
                            cliente=cliente,
                            direccion=dir_base,
                            etiqueta="Admin Registrado",
                            nombre_recibidor=nombre_recibidor or cliente.get_full_name() or cliente.username,
                            telefono_recibidor=telefono_recibidor or cliente.telefono or "0000000"
                        )
                        pedido.direccion_cliente = dir_cliente_obj
                
                pedido.save()
                return redirect('admin_pedidos')
            except Exception as e:
                error = f"Error al actualizar el pedido: {str(e)}"

    clientes = Usuario.objects.filter(tipo_usuario='CLIENTE')
    estados = EstadoPedido.objects.all()
    municipios = Municipio.objects.all().select_related('departamento')

    return render(request, 'admin_pedido_form.html', {
        'pedido': pedido,
        'clientes': clientes,
        'estados': estados,
        'municipios': municipios,
        'error': error
    })

@login_required
def admin_pedido_eliminar_view(request, pk):
    check_admin_user(request.user)
    pedido = get_object_or_404(Pedido, pk=pk)
    if request.method == 'POST':
        pedido.delete()
    return redirect('admin_pedidos')

# Nuevos ViewSets de API REST
from .models import Rol, TransaccionPasarela, TiendaAdmin
from .serializers import (
    EstadoPedidoSerializer, RolSerializer, CategoriaSerializer,
    DireccionClienteSerializer, CarritoSerializer, ItemCarritoSerializer,
    TrabajadorTiendaSerializer, TransaccionPasarelaSerializer,
    TiendaAdminSerializer
)

class EstadoPedidoViewSet(viewsets.ModelViewSet):
    queryset = EstadoPedido.objects.all()
    serializer_class = EstadoPedidoSerializer
    permission_classes = [permissions.IsAuthenticated]

class RolViewSet(viewsets.ModelViewSet):
    queryset = Rol.objects.all()
    serializer_class = RolSerializer
    permission_classes = [permissions.IsAuthenticated]

class CategoriaViewSet(viewsets.ModelViewSet):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer
    permission_classes = [permissions.IsAuthenticated]

class DireccionClienteViewSet(viewsets.ModelViewSet):
    queryset = DireccionCliente.objects.all()
    serializer_class = DireccionClienteSerializer
    permission_classes = [permissions.IsAuthenticated]

class CarritoViewSet(viewsets.ModelViewSet):
    queryset = Carrito.objects.all()
    serializer_class = CarritoSerializer
    permission_classes = [permissions.IsAuthenticated]

class ItemCarritoViewSet(viewsets.ModelViewSet):
    queryset = ItemCarrito.objects.all()
    serializer_class = ItemCarritoSerializer
    permission_classes = [permissions.IsAuthenticated]

class TrabajadorTiendaViewSet(viewsets.ModelViewSet):
    queryset = TrabajadorTienda.objects.all()
    serializer_class = TrabajadorTiendaSerializer
    permission_classes = [permissions.IsAuthenticated]

class TransaccionPasarelaViewSet(viewsets.ModelViewSet):
    queryset = TransaccionPasarela.objects.all()
    serializer_class = TransaccionPasarelaSerializer
    permission_classes = [permissions.IsAuthenticated]

class TiendaAdminViewSet(viewsets.ModelViewSet):
    queryset = TiendaAdmin.objects.all()
    serializer_class = TiendaAdminSerializer
    permission_classes = [permissions.IsAuthenticated]
