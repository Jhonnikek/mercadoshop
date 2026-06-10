from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.http import require_POST
from django.contrib.auth.models import User
from django.db.models import Count, Sum, F, DecimalField
from django.db.models.functions import Coalesce
from django.shortcuts import aget_object_or_404
from asgiref.sync import sync_to_async

from .models import Tienda
from tiendas.models import Producto

@staff_member_required(login_url='login')
async def dashboard(request): # ASYNC: async def
    total_tiendas = await Tienda.objects.acount() # ASYNC: acount()
    tiendas_activas = await Tienda.objects.filter(activo=True).acount() # ASYNC: acount()
    total_productos = await Producto.objects.acount() # ASYNC: acount()

    return render(request, 'panel_admin/dashboard.html', {
        'total_tiendas': total_tiendas,
        'tiendas_activas': tiendas_activas,
        'total_productos': total_productos,
    })

@staff_member_required(login_url='login')
async def gestionarTiendas(request): # ASYNC: async def
    tiendas_qs = (
        Tienda.objects.all()
        .annotate(num_productos=Count('productos'))
        .order_by('-id')
    )
    # ASYNC: Iteración asíncrona sobre queryset
    tiendas = [t async for t in tiendas_qs]
    
    return render(request, 'panel_admin/gestionar_tiendas.html', {
        'tiendas': tiendas,
    })

@staff_member_required(login_url='login')
@require_POST
async def crearTiendaAjax(request): # ASYNC: async def
    nombre = request.POST.get('nombre')
    direccion = request.POST.get('direccion')
    username = request.POST.get('username')
    password = request.POST.get('password')
    activo = request.POST.get('activo') != 'false'
    
    if nombre and direccion and username and password:
        if await User.objects.filter(username=username).aexists(): # ASYNC: aexists()
            return JsonResponse({'status': 'error', 'message': 'El usuario ya existe'}, status=400)
            
        # ASYNC: Uso de sync_to_async para create_user
        user = await sync_to_async(User.objects.create_user)(username=username, password=password)
        tienda = await Tienda.objects.acreate(nombre=nombre, direccion=direccion, usuario=user, activo=activo) # ASYNC: acreate()
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
async def editarTiendaAjax(request, id): # ASYNC: async def
    tienda = await aget_object_or_404(Tienda, id=id) # ASYNC: aget_object_or_404
    if request.method == 'POST':
        tienda.nombre = request.POST.get('nombre', tienda.nombre)
        tienda.direccion = request.POST.get('direccion', tienda.direccion)
        tienda.activo = request.POST.get('activo') == 'true'
        await tienda.asave() # ASYNC: asave()
        
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # ASYNC: sync_to_async para acceder a ForeignKey
        try:
            usuario = await sync_to_async(lambda: tienda.usuario)()
        except User.DoesNotExist:
            usuario = None

        if usuario:
            if username and username != usuario.username:
                if await User.objects.filter(username=username).exclude(id=usuario.id).aexists(): # ASYNC: aexists()
                    return JsonResponse({'status': 'error', 'message': 'El nombre de usuario ya está en uso'}, status=400)
                usuario.username = username
            if password:
                await sync_to_async(usuario.set_password)(password) # ASYNC: sync_to_async()
            await usuario.asave() # ASYNC: asave()
            
        num_productos = await tienda.productos.acount() # ASYNC: acount()
        return JsonResponse({
            'status': 'success',
            'id': tienda.id,
            'nombre': tienda.nombre,
            'direccion': tienda.direccion,
            'activo': tienda.activo,
            'username': usuario.username if usuario else '',
            'num_productos': num_productos,
        })
    return JsonResponse({'status': 'error'}, status=400)

@staff_member_required(login_url='login')
@require_POST
async def eliminarTiendaAjax(request, id): # ASYNC: async def
    tienda = await aget_object_or_404(Tienda, id=id) # ASYNC: aget_object_or_404
    if request.method == 'POST':
        try:
            usuario = await sync_to_async(lambda: tienda.usuario)() # ASYNC: leer ForeignKey
        except User.DoesNotExist:
            usuario = None
            
        if usuario:
            await usuario.adelete() # ASYNC: adelete()
        await tienda.adelete() # ASYNC: adelete()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)

@staff_member_required(login_url='login')
async def detalleTiendaAjax(request, id): # ASYNC: async def
    """Detalle completo de una tienda: info general + métricas + lista de productos."""
    tienda = await aget_object_or_404(Tienda, id=id) # ASYNC: aget_object_or_404
    productos = tienda.productos.all().order_by('-id')

    # Métricas de inventario
    stats = await productos.aaggregate( # ASYNC: aaggregate()
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
        async for p in productos # ASYNC: iteración asíncrona
    ]

    try:
        usuario = await sync_to_async(lambda: tienda.usuario)() # ASYNC: leer ForeignKey
    except User.DoesNotExist:
        usuario = None

    num_productos = await productos.acount() # ASYNC: acount()

    return JsonResponse({
        'status': 'success',
        'tienda': {
            'id': tienda.id,
            'nombre': tienda.nombre,
            'direccion': tienda.direccion,
            'username': usuario.username if usuario else 'Sin usuario',
            'fecha_creacion': tienda.fecha_creacion.strftime('%d/%m/%Y %H:%M') if tienda.fecha_creacion else 'Desconocida',
            'activo': tienda.activo,
            'num_productos': num_productos,
            'total_stock': stats['total_stock'],
            'valor_inventario': str(stats['valor_inventario']),
        },
        'productos': productos_data,
    })

@staff_member_required(login_url='login')
async def listarProductosGlobalAjax(request): # ASYNC: async def
    """Lista todos los productos del marketplace con info de su tienda (para popup del dashboard)."""
    productos = (
        Producto.objects.select_related('tienda')
        .all()
        .order_by('-id')
    )
    
    # ASYNC: Envoltura sincrónica para extraer foreign key 'tienda' sin errores N+1 en async
    @sync_to_async
    def extract_productos(qs):
        return [
            {
                'id': p.id,
                'nombre': p.nombre,
                'precio': str(p.precio),
                'stock': p.stock,
                'tienda_nombre': p.tienda.nombre,
                'tienda_id': p.tienda.id,
                'tienda_activa': p.tienda.activo,
            }
            for p in qs
        ]
        
    data = await extract_productos(productos)
    return JsonResponse({'status': 'success', 'productos': data})

@staff_member_required(login_url='login')
async def listarTiendasGlobalAjax(request): # ASYNC: async def
    """Lista todas las tiendas con métricas resumidas (para popup del dashboard)."""
    tiendas = (
        Tienda.objects.all()
        .annotate(
            num_productos=Count('productos'),
            total_stock=Coalesce(Sum('productos__stock'), 0),
        )
        .order_by('-id')
    )
    
    # ASYNC: Envoltura sincrónica para acceder al usuario ForeignKey en el listado
    @sync_to_async
    def extract_tiendas(qs):
        return [
            {
                'id': t.id,
                'nombre': t.nombre,
                'direccion': t.direccion,
                'activo': t.activo,
                'username': t.usuario.username if t.usuario else 'Sin usuario',
                'num_productos': t.num_productos,
                'total_stock': t.total_stock,
            }
            for t in qs
        ]
        
    data = await extract_tiendas(tiendas)
    return JsonResponse({'status': 'success', 'tiendas': data})
