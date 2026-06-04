from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.http import require_POST
from django.contrib.auth.models import User
from .models import Tienda
from tiendas.models import Producto

@staff_member_required(login_url='login')
def dashboard(request):
    total_tiendas = Tienda.objects.count()
    total_productos = Producto.objects.count()
    return render(request, 'panel_admin/dashboard.html', {
        'total_tiendas': total_tiendas,
        'total_productos': total_productos,
    })

@staff_member_required(login_url='login')
def gestionarTiendas(request):
    tiendas = Tienda.objects.all().order_by('-id')
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
        return JsonResponse({'status': 'success', 'id': tienda.id, 'nombre': tienda.nombre, 'direccion': tienda.direccion, 'activo': tienda.activo, 'username': user.username})
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
            
        return JsonResponse({'status': 'success', 'id': tienda.id, 'nombre': tienda.nombre, 'direccion': tienda.direccion, 'activo': tienda.activo, 'username': tienda.usuario.username if tienda.usuario else ''})
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
    tienda = get_object_or_404(Tienda, id=id)
    return JsonResponse({
        'status': 'success',
        'tienda': {
            'id': tienda.id,
            'nombre': tienda.nombre,
            'direccion': tienda.direccion,
            'username': tienda.usuario.username if tienda.usuario else 'Sin usuario',
            'fecha_creacion': tienda.fecha_creacion.strftime('%d/%m/%Y %H:%M') if tienda.fecha_creacion else 'Desconocida',
            'activo': tienda.activo
        }
    })
