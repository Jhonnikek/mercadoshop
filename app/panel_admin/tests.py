import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from panel_admin.models import Tienda
from tiendas.models import Producto
from django.test import AsyncClient

# ASYNC: Tests asíncronos para las vistas refactorizadas
@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_dashboard_async():
    client = AsyncClient()
    user = await User.objects.acreate_user(username="admin_test", password="password", is_staff=True)
    await client.aforce_login(user)

    response = await client.aget(reverse('dashboard'))
    assert response.status_code == 200

@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_crear_tienda_ajax_async():
    client = AsyncClient()
    user = await User.objects.acreate_user(username="admin_test2", password="password", is_staff=True)
    await client.aforce_login(user)

    response = await client.apost(reverse('crear_tienda'), {
        'nombre': 'Tienda de Prueba',
        'direccion': 'Calle Falsa 123',
        'username': 'vendedor1',
        'password': 'password',
        'activo': 'true'
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data['status'] == 'success'
    assert await Tienda.objects.filter(nombre='Tienda de Prueba').aexists()

@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_listar_tiendas_global_ajax_async():
    client = AsyncClient()
    user = await User.objects.acreate_user(username="admin_test3", password="password", is_staff=True)
    await client.aforce_login(user)

    vendedor = await User.objects.acreate_user(username="vendedor2", password="password")
    await Tienda.objects.acreate(nombre="Tienda Global", direccion="Dir Global", usuario=vendedor)

    response = await client.aget(reverse('listar_tiendas_global'))
    assert response.status_code == 200
    data = response.json()
    assert data['status'] == 'success'
    assert len(data['tiendas']) >= 1
