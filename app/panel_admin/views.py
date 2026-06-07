from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.http import require_POST
from django.contrib.auth.models import User
from django.db.models import Count, Sum, F, DecimalField
from django.db.models.functions import Coalesce
from .models import Tienda
from tiendas.models import Producto

@staff_member_required(login_url='login')
def dashboard(request):
    total_tiendas = Tienda.objects.count()
    tiendas_activas = Tienda.objects.filter(activo=True).count()
    total_productos = Producto.objects.count()

    return render(request, 'panel_admin/dashboard.html', {
        'total_tiendas': total_tiendas,
        'tiendas_activas': tiendas_activas,
        'total_productos': total_productos,
    })

@staff_member_required(login_url='login')
def gestionarTiendas(request):
    tiendas = (
        Tienda.objects.all()
        .annotate(num_productos=Count('productos'))
        .order_by('-id')
    )
    return render(request, 'panel_admin/gestionar_tiendas.html', {
        'tiendas': tiendas,
    })

@staff_member_required(login_url='login')
@require_POST
def crearTiendaAjax(request):
    nombre = request.POST.get('nombre')
    direccion = request.POST.get('direccion')
    username = request.POST.get('username')
    password = request.POST.get('password')
    activo = request.POST.get('activo') != 'false'
    
    if nombre and direccion and username and password:
        if User.objects.filter(username=username).exists():
            return JsonResponse({'status': 'error', 'message': 'El usuario ya existe'}, status=400)
            
        user = User.objects.create_user(username=username, password=password)
        tienda = Tienda.objects.create(nombre=nombre, direccion=direccion, usuario=user, activo=activo)
        return JsonResponse({
            'status': 'success',
            'id': tienda.id,
            'nombre': tienda.nombre,
            'direccion': tienda.direccion,
            'activo': tienda.activo,
            'username': user.username,
            'num_productos': 0,
        })
    return JsonResponse({'status': 'error', 'message': 'Faltan campos requeridos'}, status=400)

@staff_member_required(login_url='login')
@require_POST
def editarTiendaAjax(request, id):
    tienda = get_object_or_404(Tienda, id=id)
    if request.method == 'POST':
        tienda.nombre = request.POST.get('nombre', tienda.nombre)
        tienda.direccion = request.POST.get('direccion', tienda.direccion)
        tienda.activo = request.POST.get('activo') == 'true'
        tienda.save()
        
        username = request.POST.get('username')
        password = request.POST.get('password')
        if tienda.usuario:
            if username and username != tienda.usuario.username:
                if User.objects.filter(username=username).exclude(id=tienda.usuario.id).exists():
                    return JsonResponse({'status': 'error', 'message': 'El nombre de usuario ya está en uso'}, status=400)
                tienda.usuario.username = username
            if password:
                tienda.usuario.set_password(password)
            tienda.usuario.save()
            
        return JsonResponse({
            'status': 'success',
            'id': tienda.id,
            'nombre': tienda.nombre,
            'direccion': tienda.direccion,
            'activo': tienda.activo,
            'username': tienda.usuario.username if tienda.usuario else '',
            'num_productos': tienda.productos.count(),
        })
    return JsonResponse({'status': 'error'}, status=400)

@staff_member_required(login_url='login')
@require_POST
def eliminarTiendaAjax(request, id):
    tienda = get_object_or_404(Tienda, id=id)
    if request.method == 'POST':
        if tienda.usuario:
            tienda.usuario.delete()
        tienda.delete()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)

@staff_member_required(login_url='login')
def detalleTiendaAjax(request, id):
    """Detalle completo de una tienda: info general + métricas + lista de productos."""
    tienda = get_object_or_404(Tienda, id=id)
    productos = tienda.productos.all().order_by('-id')

    # Métricas de inventario
    stats = productos.aggregate(
        total_stock=Coalesce(Sum('stock'), 0),
        valor_inventario=Coalesce(
            Sum(F('precio') * F('stock'), output_field=DecimalField()),
            0,
            output_field=DecimalField(),
        ),
    )

    productos_data = [
        {
            'id': p.id,
            'nombre': p.nombre,
            'precio': str(p.precio),
            'stock': p.stock,
            'descripcion': p.descripcion or '',
        }
        for p in productos
    ]

    return JsonResponse({
        'status': 'success',
        'tienda': {
            'id': tienda.id,
            'nombre': tienda.nombre,
            'direccion': tienda.direccion,
            'username': tienda.usuario.username if tienda.usuario else 'Sin usuario',
            'fecha_creacion': tienda.fecha_creacion.strftime('%d/%m/%Y %H:%M') if tienda.fecha_creacion else 'Desconocida',
            'activo': tienda.activo,
            'num_productos': productos.count(),
            'total_stock': stats['total_stock'],
            'valor_inventario': str(stats['valor_inventario']),
        },
        'productos': productos_data,
    })

@staff_member_required(login_url='login')
def listarProductosGlobalAjax(request):
    """Lista todos los productos del marketplace con info de su tienda (para popup del dashboard)."""
    productos = (
        Producto.objects.select_related('tienda')
        .all()
        .order_by('-id')
    )
    data = [
        {
            'id': p.id,
            'nombre': p.nombre,
            'precio': str(p.precio),
            'stock': p.stock,
            'tienda_nombre': p.tienda.nombre,
            'tienda_id': p.tienda.id,
            'tienda_activa': p.tienda.activo,
        }
        for p in productos
    ]
    return JsonResponse({'status': 'success', 'productos': data})

@staff_member_required(login_url='login')
def listarTiendasGlobalAjax(request):
    """Lista todas las tiendas con métricas resumidas (para popup del dashboard)."""
    tiendas = (
        Tienda.objects.all()
        .annotate(
            num_productos=Count('productos'),
            total_stock=Coalesce(Sum('productos__stock'), 0),
        )
        .order_by('-id')
    )
    data = [
        {
            'id': t.id,
            'nombre': t.nombre,
            'direccion': t.direccion,
            'activo': t.activo,
            'username': t.usuario.username if t.usuario else 'Sin usuario',
            'num_productos': t.num_productos,
            'total_stock': t.total_stock,
        }
        for t in tiendas
    ]
    return JsonResponse({'status': 'success', 'tiendas': data})
