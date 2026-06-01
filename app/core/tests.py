from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import Usuario, Tienda, Producto, TrabajadorTienda, Pedido, EstadoPedido, Categoria, Direccion, Municipio, Departamento, DireccionCliente, Carrito, ItemCarrito

class MercadoShopAPITests(APITestCase):

    def setUp(self):
        # 1. Configurar Localizaciones
        depto = Departamento.objects.create(nombre="Cundinamarca", codigo_dane="25")
        muni = Municipio.objects.create(departamento=depto, nombre="Bogotá", codigo_dane="25001")
        dir_tienda_a = Direccion.objects.create(nomenclatura="Calle 100", barrio="Chico", municipio=muni)
        dir_tienda_b = Direccion.objects.create(nomenclatura="Calle 72", barrio="Chapinero", municipio=muni)
        
        # 2. Configurar Tiendas
        self.tienda_a = Tienda.objects.create(
            nombre_comercial="Tienda A", correo_atencion="a@tienda.com", 
            telefono_atencion="123", razon_social="A SAS", direccion=dir_tienda_a, estado_tienda="Activa"
        )
        self.tienda_b = Tienda.objects.create(
            nombre_comercial="Tienda B", correo_atencion="b@tienda.com", 
            telefono_atencion="456", razon_social="B SAS", direccion=dir_tienda_b, estado_tienda="Activa"
        )
        
        # 3. Configurar Categoría y Productos
        cat = Categoria.objects.create(nombre_categoria="Tecnología", estado=True)
        self.prod_a = Producto.objects.create(
            tienda=self.tienda_a, descripcion_corta="Celular A", 
            categoria=cat, precio_unitario=1000.0, cantidad_stock=5
        )
        self.prod_b = Producto.objects.create(
            tienda=self.tienda_b, descripcion_corta="Laptop B", 
            categoria=cat, precio_unitario=2000.0, cantidad_stock=5
        )
        
        # 4. Configurar Estado Pedido
        self.estado = EstadoPedido.objects.create(nombre_estado="Creado")
        
        # 5. Configurar Usuarios
        self.admin = Usuario.objects.create_superuser(username="admin_user", password="password", tipo_usuario="ADMIN")
        self.cliente = Usuario.objects.create_user(username="cliente_user", password="password", tipo_usuario="CLIENTE")
        self.trabajador_a = Usuario.objects.create_user(username="trabajador_a", password="password", tipo_usuario="TRABAJADOR")
        self.trabajador_b = Usuario.objects.create_user(username="trabajador_b", password="password", tipo_usuario="TRABAJADOR")
        
        # 6. Vincular Trabajador A a Tienda A, y Trabajador B a Tienda B
        TrabajadorTienda.objects.create(tienda=self.tienda_a, trabajador=self.trabajador_a)
        TrabajadorTienda.objects.create(tienda=self.tienda_b, trabajador=self.trabajador_b)

    def test_admin_puede_ver_todo(self):
        """Admin global puede ver todos los productos y tiendas"""
        self.client.force_authenticate(user=self.admin)
        
        # Tiendas
        response = self.client.get(reverse('tienda-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        
        # Productos
        response = self.client.get(reverse('producto-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_trabajador_aislamiento_productos(self):
        """El trabajador de la Tienda A solo puede ver productos de la Tienda A"""
        self.client.force_authenticate(user=self.trabajador_a)
        
        response = self.client.get(reverse('producto-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Solo debe ver el Celular A de la Tienda A, no la Laptop B de la Tienda B
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['descripcion_corta'], "Celular A")

    def test_trabajador_no_puede_crear_producto_para_otra_tienda(self):
        """El trabajador de la Tienda A no puede crear un producto para la Tienda B"""
        self.client.force_authenticate(user=self.trabajador_a)
        
        data = {
            "tienda": self.tienda_b.id,
            "descripcion_corta": "Celular Infiltrado",
            "precio_unitario": "500.0000",
            "cantidad_stock": 10
        }
        response = self.client.post(reverse('producto-list'), data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # Pruebas para las nuevas vistas y plantillas dinámicas
    def test_registro_cliente_exitoso(self):
        """Registro exitoso de un cliente redirige al panel"""
        data = {
            "tipo_usuario": "CLIENTE",
            "name": "Juan Perez",
            "email": "juan@perez.com",
            "password": "securepassword123"
        }
        # Usar la sesión HTTP estándar del cliente de pruebas de Django
        response = self.client.post(reverse('register'), data)
        self.assertEqual(response.status_code, 302) # Redirección
        self.assertTrue(Usuario.objects.filter(email="juan@perez.com").exists())
        user = Usuario.objects.get(email="juan@perez.com")
        self.assertEqual(user.first_name, "Juan")
        self.assertEqual(user.last_name, "Perez")
        self.assertEqual(user.tipo_usuario, "CLIENTE")

    def test_registro_trabajador_con_tienda_exitoso(self):
        """Registro de dueño de tienda crea la tienda y vinculación atómicamente"""
        data = {
            "tipo_usuario": "TRABAJADOR",
            "store_name": "Mi Nueva Tienda",
            "name": "Maria Gomez",
            "email": "maria@gomez.com",
            "password": "securepassword123"
        }
        response = self.client.post(reverse('register'), data)
        self.assertEqual(response.status_code, 302)
        
        # Validar creación del usuario y tienda
        self.assertTrue(Usuario.objects.filter(email="maria@gomez.com").exists())
        user = Usuario.objects.get(email="maria@gomez.com")
        self.assertEqual(user.tipo_usuario, "TRABAJADOR")
        
        self.assertTrue(Tienda.objects.filter(nombre_comercial="Mi Nueva Tienda").exists())
        tienda = Tienda.objects.get(nombre_comercial="Mi Nueva Tienda")
        
        # Validar vinculación
        self.assertTrue(TrabajadorTienda.objects.filter(trabajador=user, tienda=tienda).exists())

    def test_producto_detalle_view(self):
        """La vista de detalle del producto carga correctamente"""
        response = self.client.get(reverse('producto_detalle', args=[self.prod_a.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Celular A")

    def test_perfil_settings_view_get_y_post(self):
        """Se puede cargar y actualizar la configuración de perfil y dirección"""
        # Login
        self.client.login(username="cliente_user", password="password")
        
        # GET
        response = self.client.get(reverse('perfil_settings'))
        self.assertEqual(response.status_code, 200)
        
        # POST
        data = {
            "first_name": "Client",
            "last_name": "Updated",
            "email": "cliente_new@user.com",
            "telefono": "555-5555",
            "nomenclatura": "Calle Falsa 123",
            "barrio": "Springfield",
            "codigo_postal": "9999"
        }
        response = self.client.post(reverse('perfil_settings'), data)
        self.assertEqual(response.status_code, 200)
        
        # Validar persistencia
        self.cliente.refresh_from_db()
        self.assertEqual(self.cliente.first_name, "Client")
        self.assertEqual(self.cliente.direccion_principal.nomenclatura, "Calle Falsa 123")

    def test_tienda_publico_view(self):
        """El storefront público carga los productos de la tienda correspondiente"""
        response = self.client.get(reverse('tienda_publico', args=[self.tienda_a.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Tienda A")
        self.assertContains(response, "Celular A")
        # No debe contener productos de la tienda B
        self.assertNotContains(response, "Laptop B")

    def test_inventario_trabajador_restricciones_y_aislamiento(self):
        """Aislamiento multi-tenant en la vista de inventario"""
        # 1. Cliente no debe poder ver el inventario (lanza PermissionDenied / 403)
        self.client.login(username="cliente_user", password="password")
        response = self.client.get(reverse('inventario_trabajador'))
        self.assertEqual(response.status_code, 403)
        
        # 2. Trabajador A solo ve productos de su Tienda A
        self.client.login(username="trabajador_a", password="password")
        response = self.client.get(reverse('inventario_trabajador'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Celular A")
        self.assertNotContains(response, "Laptop B")

    def test_historial_pedidos_trabajador_vs_cliente(self):
        """Aislamiento multi-tenant en el historial de pedidos"""
        # Crear un pedido para el cliente con el producto A
        pedido = Pedido.objects.create(
            cliente=self.cliente,
            numero_comprobante="PED-TEST-1",
            subtotal=1000.0,
            costo_envio=50.0,
            total=1050.0,
            estado_pedido=self.estado
        )
        from .models import DetallePedido
        DetallePedido.objects.create(
            pedido=pedido,
            producto=self.prod_a,
            nombre_producto="Celular A",
            precio_compra=1000.0,
            cantidad=1,
            subtotal=1000.0
        )
        
        # 1. Cliente ve su propio pedido
        self.client.login(username="cliente_user", password="password")
        response = self.client.get(reverse('historial_pedidos'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "PED-TEST-1")
        
        # 2. Trabajador A (de tienda A) ve el pedido porque contiene su producto Celular A
        self.client.login(username="trabajador_a", password="password")
        response = self.client.get(reverse('historial_pedidos'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "PED-TEST-1")
        
        # 3. Trabajador B (de tienda B) no ve el pedido porque es de la tienda A
        self.client.login(username="trabajador_b", password="password")
        response = self.client.get(reverse('historial_pedidos'))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "PED-TEST-1")

    def test_api_endpoints_departamento_municipio_direccion(self):
        """Verifica que los endpoints REST de departamentos, municipios y direcciones funcionan"""
        self.client.force_authenticate(user=self.admin)
        
        # 1. Departamentos API
        response = self.client.get(reverse('departamento-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 2. Municipios API
        response = self.client.get(reverse('municipio-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 3. Direcciones API
        response = self.client.get(reverse('direccion-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_producto_crear_y_editar_exitoso(self):
        """Un trabajador puede crear y editar productos de su tienda"""
        self.client.login(username="trabajador_a", password="password")
        
        # Crear
        data = {
            "descripcion_corta": "Nuevo Celular A",
            "categoria": Categoria.objects.first().id,
            "marca": "Nokia",
            "descripcion_larga": "Detalles del Nokia",
            "precio_unitario": "599.99",
            "cantidad_stock": "10",
            "url_imagen_principal": "http://nokia.img"
        }
        response = self.client.post(reverse('producto_crear'), data)
        self.assertEqual(response.status_code, 302) # Redirige a inventario
        self.assertTrue(Producto.objects.filter(descripcion_corta="Nuevo Celular A", tienda=self.tienda_a).exists())
        
        # Editar
        new_prod = Producto.objects.get(descripcion_corta="Nuevo Celular A")
        edit_data = {
            "descripcion_corta": "Celular A Modificado",
            "categoria": Categoria.objects.first().id,
            "marca": "Nokia Editado",
            "descripcion_larga": "Detalles modificados",
            "precio_unitario": "550.00",
            "cantidad_stock": "5",
            "url_imagen_principal": "http://nokia.img"
        }
        response = self.client.post(reverse('producto_editar', args=[new_prod.id]), edit_data)
        self.assertEqual(response.status_code, 302)
        new_prod.refresh_from_db()
        self.assertEqual(new_prod.descripcion_corta, "Celular A Modificado")
        self.assertEqual(new_prod.precio_unitario, 550.00)

    def test_producto_crear_y_editar_restringido(self):
        """Clientes no pueden crear ni editar. Trabajador B no puede editar prod_a de Tienda A"""
        # Cliente crear
        self.client.login(username="cliente_user", password="password")
        response = self.client.post(reverse('producto_crear'), {})
        self.assertEqual(response.status_code, 403) # PermissionDenied
        
        # Trabajador B editar prod_a
        self.client.login(username="trabajador_b", password="password")
        response = self.client.post(reverse('producto_editar', args=[self.prod_a.id]), {
            "descripcion_corta": "Intento de Hack",
            "categoria": Categoria.objects.first().id,
            "precio_unitario": "1.0",
            "cantidad_stock": "1"
        })
        self.assertEqual(response.status_code, 403)

    def test_producto_eliminar_exitoso_y_restringido(self):
        """Trabajadores solo pueden eliminar productos de su tienda"""
        # Trabajador B intenta eliminar prod_a de Tienda A
        self.client.login(username="trabajador_b", password="password")
        response = self.client.post(reverse('producto_eliminar', args=[self.prod_a.id]))
        self.assertEqual(response.status_code, 403)
        self.assertTrue(Producto.objects.filter(id=self.prod_a.id).exists())
        
        # Trabajador A elimina prod_a
        self.client.login(username="trabajador_a", password="password")
        response = self.client.post(reverse('producto_eliminar', args=[self.prod_a.id]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Producto.objects.filter(id=self.prod_a.id).exists())

    def test_pedido_detalle_trabajador_acceso_y_actualizar_estado(self):
        """Trabajador accede y actualiza estado de pedidos que contienen productos de su tienda"""
        pedido = Pedido.objects.create(
            cliente=self.cliente,
            numero_comprobante="PED-TEST-3",
            subtotal=1000.0,
            costo_envio=50.0,
            total=1050.0,
            estado_pedido=self.estado
        )
        from .models import DetallePedido
        DetallePedido.objects.create(
            pedido=pedido,
            producto=self.prod_a,
            nombre_producto="Celular A",
            precio_compra=1000.0,
            cantidad=1,
            subtotal=1000.0
        )
        
        # Trabajador B no puede acceder (no tiene productos de Tienda B)
        self.client.login(username="trabajador_b", password="password")
        response = self.client.get(reverse('pedido_detalle_trabajador', args=[pedido.id]))
        self.assertEqual(response.status_code, 403)
        
        # Trabajador A accede y actualiza
        self.client.login(username="trabajador_a", password="password")
        response = self.client.get(reverse('pedido_detalle_trabajador', args=[pedido.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "PED-TEST-3")
        
        nuevo_estado = EstadoPedido.objects.create(nombre_estado="Listo para Enviar")
        response = self.client.post(reverse('pedido_detalle_trabajador', args=[pedido.id]), {
            "estado_id": nuevo_estado.id
        })
        self.assertEqual(response.status_code, 200)
        pedido.refresh_from_db()
        self.assertEqual(pedido.estado_pedido, nuevo_estado)

    def test_pedido_detalle_cliente_acceso(self):
        """Cliente puede ver el seguimiento de su propio pedido, pero no el de otros"""
        pedido = Pedido.objects.create(
            cliente=self.cliente,
            numero_comprobante="PED-TEST-4",
            subtotal=1000.0,
            costo_envio=50.0,
            total=1050.0,
            estado_pedido=self.estado
        )
        
        # Trabajador A no puede acceder a seguimiento de cliente si no es el cliente
        self.client.login(username="trabajador_a", password="password")
        response = self.client.get(reverse('pedido_detalle_cliente', args=[pedido.id]))
        self.assertEqual(response.status_code, 403)
        
        # Cliente sí accede
        self.client.login(username="cliente_user", password="password")
        response = self.client.get(reverse('pedido_detalle_cliente', args=[pedido.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "PED-TEST-4")

    def test_admin_paneles_tiendas_y_usuarios_gestion(self):
        """Admin puede ver tiendas y usuarios y suspenderlos/activarlos"""
        self.client.login(username="admin_user", password="password")
        
        # Gestión de tiendas
        response = self.client.get(reverse('admin_tiendas'))
        self.assertEqual(response.status_code, 200)
        
        # Suspender tienda
        response = self.client.post(reverse('admin_tiendas'), {
            "tienda_id": self.tienda_a.id,
            "action": "suspend"
        })
        self.assertEqual(response.status_code, 302)
        self.tienda_a.refresh_from_db()
        self.assertEqual(self.tienda_a.estado_tienda, "Suspendida")
        
        # Activar tienda
        response = self.client.post(reverse('admin_tiendas'), {
            "tienda_id": self.tienda_a.id,
            "action": "activate"
        })
        self.assertEqual(response.status_code, 302)
        self.tienda_a.refresh_from_db()
        self.assertEqual(self.tienda_a.estado_tienda, "Activa")
        
        # Gestión de usuarios
        response = self.client.get(reverse('admin_usuarios'))
        self.assertEqual(response.status_code, 200)
        
        # Suspender usuario
        response = self.client.post(reverse('admin_usuarios'), {
            "user_to_toggle_id": self.cliente.id,
            "action": "suspend"
        })
        self.assertEqual(response.status_code, 302)
        self.cliente.refresh_from_db()
        self.assertFalse(self.cliente.is_active)
        
        # Activar usuario
        response = self.client.post(reverse('admin_usuarios'), {
            "user_to_toggle_id": self.cliente.id,
            "action": "activate"
        })
        self.assertEqual(response.status_code, 302)
        self.cliente.refresh_from_db()
        self.assertTrue(self.cliente.is_active)

    def test_catalogo_busqueda_y_filtros(self):
        """Verifica que el catálogo filtre correctamente por query y categoría"""
        # Sin filtros
        response = self.client.get(reverse('catalogo'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Celular A")
        self.assertContains(response, "Laptop B")
        
        # Con filtro q
        response = self.client.get(reverse('catalogo') + "?q=Celular")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Celular A")
        self.assertNotContains(response, "Laptop B")


class MercadoShopCarritoTests(APITestCase):

    def setUp(self):
        # Localizaciones
        self.depto = Departamento.objects.create(nombre="Antioquia", codigo_dane="05")
        self.muni = Municipio.objects.create(departamento=self.depto, nombre="Medellín", codigo_dane="05001")
        self.dir_tienda = Direccion.objects.create(nomenclatura="Calle 10", barrio="Poblado", municipio=self.muni)
        
        # Tienda
        self.tienda = Tienda.objects.create(
            nombre_comercial="Tienda Test", correo_atencion="t@test.com", 
            telefono_atencion="123", razon_social="Test SAS", direccion=self.dir_tienda, estado_tienda="Activa"
        )
        
        # Categoria & Producto
        cat = Categoria.objects.create(nombre_categoria="Tecnología", estado=True)
        self.prod = Producto.objects.create(
            tienda=self.tienda, descripcion_corta="Celular X", 
            categoria=cat, precio_unitario=1000.0, cantidad_stock=5
        )
        
        # Estado Pedido
        self.estado = EstadoPedido.objects.create(nombre_estado="Creado")
        
        # Usuario Cliente
        self.cliente = Usuario.objects.create_user(username="cliente_carrito", password="password", tipo_usuario="CLIENTE")
        
        # Direccion del Cliente
        self.dir_envio = DireccionCliente.objects.create(
            cliente=self.cliente,
            direccion=self.dir_tienda,
            etiqueta="Casa",
            nombre_recibidor="Test Recibidor",
            telefono_recibidor="3001112223"
        )

    def test_flujo_completo_carrito_y_checkout(self):
        """Verifica el ciclo de vida completo del carrito y la creación de un pedido"""
        self.client.login(username="cliente_carrito", password="password")
        
        # 1. Agregar al carrito
        response = self.client.post(reverse('agregar_al_carrito', args=[self.prod.id]), {'cantidad': 2})
        self.assertEqual(response.status_code, 302) # Redirige al detalle de carrito
        
        # Verificar que se creó el carrito y el ítem
        carrito = Carrito.objects.get(cliente=self.cliente, estado='Activo')
        self.assertEqual(carrito.items.count(), 1)
        item = carrito.items.first()
        self.assertEqual(item.producto, self.prod)
        self.assertEqual(item.cantidad, 2)
        
        # 2. Ver detalle del carrito
        response = self.client.get(reverse('carrito_detalle'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Celular X")
        self.assertContains(response, "2") # Cantidad
        
        # 3. Incrementar cantidad
        response = self.client.post(reverse('actualizar_item_carrito', args=[item.id]), {'accion': 'incrementar'})
        self.assertEqual(response.status_code, 302)
        item.refresh_from_db()
        self.assertEqual(item.cantidad, 3)
        
        # 4. Realizar pedido (Checkout GET)
        response = self.client.get(reverse('realizar_pedido'))
        self.assertEqual(response.status_code, 200)
        
        # 5. Confirmar pedido (Checkout POST con dirección existente)
        response = self.client.post(reverse('realizar_pedido'), {'direccion_id': self.dir_envio.id})
        self.assertEqual(response.status_code, 302) # Redirige a éxito
        
        # Verificar que el pedido fue creado
        self.assertTrue(Pedido.objects.filter(cliente=self.cliente).exists())
        pedido = Pedido.objects.get(cliente=self.cliente)
        self.assertEqual(pedido.total, 3000.0 + 10000.0) # 3 * 1000 + 10000 envio
        self.assertEqual(pedido.detalles.count(), 1)
        self.assertEqual(pedido.detalles.first().cantidad, 3)
        
        # Verificar que se restó del stock
        self.prod.refresh_from_db()
        self.assertEqual(self.prod.cantidad_stock, 2)
        
        # Verificar que el carrito cambió su estado
        carrito.refresh_from_db()
        self.assertEqual(carrito.estado, 'Convertido')
        
    def test_creacion_direccion_en_checkout(self):
        """Verifica que se pueda registrar una nueva dirección de envío al hacer checkout"""
        self.client.login(username="cliente_carrito", password="password")
        
        # Agregar al carrito
        self.client.post(reverse('agregar_al_carrito', args=[self.prod.id]), {'cantidad': 1})
        
        # Postear checkout con nueva dirección
        checkout_data = {
            'direccion_id': 'nueva',
            'nombre_recibidor': 'Nuevo Recibidor',
            'telefono_recibidor': '3119998888',
            'nomenclatura': 'Calle Nueva 99',
            'barrio': 'Centro',
            'etiqueta': 'Oficina',
            'municipio_id': self.muni.id
        }
        response = self.client.post(reverse('realizar_pedido'), checkout_data)
        self.assertEqual(response.status_code, 302)
        
        # Verificar que se creó la dirección
        self.assertTrue(DireccionCliente.objects.filter(cliente=self.cliente, etiqueta='Oficina').exists())
        nueva_dir = DireccionCliente.objects.get(cliente=self.cliente, etiqueta='Oficina')
        self.assertEqual(nueva_dir.nombre_recibidor, 'Nuevo Recibidor')
        self.assertEqual(nueva_dir.direccion.nomenclatura, 'Calle Nueva 99')
        
        # Verificar creación del pedido con esa dirección
        pedido = Pedido.objects.get(cliente=self.cliente)
        self.assertEqual(pedido.direccion_cliente, nueva_dir)


class MercadoShopAdminCrudTests(APITestCase):
    def setUp(self):
        # Crear estados de pedido necesarios
        self.estado_creado = EstadoPedido.objects.create(nombre_estado="Creado")
        self.estado_enviado = EstadoPedido.objects.create(nombre_estado="Enviado")
        
        # Departamentos y Municipios para direcciones
        self.depto = Departamento.objects.create(nombre="Cundinamarca")
        self.muni = Municipio.objects.create(nombre="Bogota", departamento=self.depto)

        # Crear usuarios de prueba
        self.admin_user = Usuario.objects.create_superuser(username="admin_test", password="adminpassword", email="admin@test.com")
        self.admin_user.tipo_usuario = 'ADMIN'
        self.admin_user.save()
        
        self.cliente_user = Usuario.objects.create_user(username="cliente_test", password="password", email="cliente@test.com")
        self.cliente_user.tipo_usuario = 'CLIENTE'
        self.cliente_user.save()

        self.trabajador_user = Usuario.objects.create_user(username="trabajador_test", password="password", email="trabajador@test.com")
        self.trabajador_user.tipo_usuario = 'TRABAJADOR'
        self.trabajador_user.save()

        # Tienda de prueba
        self.tienda = Tienda.objects.create(
            nombre_comercial="Tienda Test",
            correo_atencion="tiendatest@test.com",
            telefono_atencion="1234567",
            razon_social="Tienda Test S.A.S",
            estado_tienda="Activa"
        )
        
        # Producto
        self.prod = Producto.objects.create(
            tienda=self.tienda,
            descripcion_corta="Producto Test",
            precio_unitario=5000.0,
            cantidad_stock=10
        )

    def test_permission_denied_for_non_admin(self):
        """Verifica que usuarios que no son administradores no tengan acceso a las vistas de CRUD admin"""
        self.client.login(username="cliente_test", password="password")
        
        # Intentar entrar a crear usuario
        response = self.client.get(reverse('admin_usuario_crear'))
        self.assertEqual(response.status_code, 403)
        
        # Intentar entrar a crear tienda
        response = self.client.get(reverse('admin_tienda_crear'))
        self.assertEqual(response.status_code, 403)
        
        # Intentar entrar a crear pedido
        response = self.client.get(reverse('admin_pedido_crear'))
        self.assertEqual(response.status_code, 403)

    def test_admin_usuario_crud(self):
        """Verifica el flujo CRUD completo de usuarios por parte de un admin"""
        self.client.login(username="admin_test", password="adminpassword")
        
        # 1. GET crear formulario
        response = self.client.get(reverse('admin_usuario_crear'))
        self.assertEqual(response.status_code, 200)

        # 2. POST crear usuario (Trabajador vinculado a tienda)
        user_data = {
            'username': 'nuevo_trabajador',
            'password': 'newpassword123',
            'email': 'new_worker@test.com',
            'first_name': 'Carlos',
            'last_name': 'Perez',
            'tipo_usuario': 'TRABAJADOR',
            'documento': '10998877',
            'telefono': '3200000000',
            'tienda_id': self.tienda.id
        }
        response = self.client.post(reverse('admin_usuario_crear'), user_data)
        self.assertEqual(response.status_code, 302) # Redirige a lista
        
        # Verificar que existe
        self.assertTrue(Usuario.objects.filter(username='nuevo_trabajador').exists())
        nuevo_user = Usuario.objects.get(username='nuevo_trabajador')
        self.assertEqual(nuevo_user.tipo_usuario, 'TRABAJADOR')
        self.assertTrue(TrabajadorTienda.objects.filter(trabajador=nuevo_user, tienda=self.tienda).exists())

        # 3. GET editar formulario
        response = self.client.get(reverse('admin_usuario_editar', args=[nuevo_user.id]))
        self.assertEqual(response.status_code, 200)

        # 4. POST editar usuario (cambiar email y suspender)
        edit_data = {
            'username': 'nuevo_trabajador',
            'email': 'updated_worker@test.com',
            'first_name': 'Carlos Modificado',
            'last_name': 'Perez',
            'tipo_usuario': 'TRABAJADOR',
            'documento': '10998877',
            'telefono': '3200000000',
            'tienda_id': self.tienda.id,
            'is_active': '' # desmarcado = inactivo
        }
        response = self.client.post(reverse('admin_usuario_editar', args=[nuevo_user.id]), edit_data)
        self.assertEqual(response.status_code, 302)
        
        nuevo_user.refresh_from_db()
        self.assertEqual(nuevo_user.email, 'updated_worker@test.com')
        self.assertEqual(nuevo_user.first_name, 'Carlos Modificado')
        self.assertFalse(nuevo_user.is_active)

        # 5. POST eliminar usuario
        response = self.client.post(reverse('admin_usuario_eliminar', args=[nuevo_user.id]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Usuario.objects.filter(username='nuevo_trabajador').exists())

    def test_admin_tienda_crud(self):
        """Verifica el flujo CRUD completo de tiendas por parte de un admin"""
        self.client.login(username="admin_test", password="adminpassword")

        # 1. GET crear formulario
        response = self.client.get(reverse('admin_tienda_crear'))
        self.assertEqual(response.status_code, 200)

        # 2. POST crear tienda
        tienda_data = {
            'nombre_comercial': 'Nueva Tienda Cultivos',
            'razon_social': 'Cultivos del Oriente S.A.S',
            'correo_atencion': 'cultivos@test.com',
            'telefono_atencion': '9876543',
            'descripcion': 'Tienda de cultivos organicos',
            'estado_tienda': 'Activa',
            'plan_id': '2',
            'trabajador_id': self.trabajador_user.id
        }
        response = self.client.post(reverse('admin_tienda_crear'), tienda_data)
        self.assertEqual(response.status_code, 302)
        
        self.assertTrue(Tienda.objects.filter(nombre_comercial='Nueva Tienda Cultivos').exists())
        nueva_tienda = Tienda.objects.get(nombre_comercial='Nueva Tienda Cultivos')
        self.assertEqual(nueva_tienda.plan_id, 2)
        self.assertTrue(TrabajadorTienda.objects.filter(tienda=nueva_tienda, trabajador=self.trabajador_user).exists())

        # 3. GET editar formulario
        response = self.client.get(reverse('admin_tienda_editar', args=[nueva_tienda.id]))
        self.assertEqual(response.status_code, 200)

        # 4. POST editar tienda
        edit_data = {
            'nombre_comercial': 'Cultivos Organicos Editado',
            'razon_social': 'Cultivos del Oriente S.A.S',
            'correo_atencion': 'cultivos_new@test.com',
            'telefono_atencion': '9876543',
            'descripcion': 'Descripcion editada',
            'estado_tienda': 'Suspendida',
            'plan_id': '3',
            'trabajador_id': '' # Limpiar trabajador
        }
        response = self.client.post(reverse('admin_tienda_editar', args=[nueva_tienda.id]), edit_data)
        self.assertEqual(response.status_code, 302)
        
        nueva_tienda.refresh_from_db()
        self.assertEqual(nueva_tienda.nombre_comercial, 'Cultivos Organicos Editado')
        self.assertEqual(nueva_tienda.estado_tienda, 'Suspendida')
        self.assertEqual(nueva_tienda.plan_id, 3)
        self.assertFalse(TrabajadorTienda.objects.filter(tienda=nueva_tienda).exists())

        # 5. POST eliminar tienda
        response = self.client.post(reverse('admin_tienda_eliminar', args=[nueva_tienda.id]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Tienda.objects.filter(nombre_comercial='Cultivos Organicos Editado').exists())

    def test_admin_pedido_crud(self):
        """Verifica el flujo CRUD completo de pedidos/ventas por parte de un admin"""
        self.client.login(username="admin_test", password="adminpassword")

        # 1. GET lista de pedidos
        response = self.client.get(reverse('admin_pedidos'))
        self.assertEqual(response.status_code, 200)

        # 2. POST crear pedido
        pedido_data = {
            'cliente_id': self.cliente_user.id,
            'estado_pedido_id': self.estado_creado.id,
            'subtotal': '15000.00',
            'costo_envio': '5000.00',
            'total': '20000.00',
            
            # Direccion
            'nombre_recibidor': 'Carlos Recibe',
            'telefono_recibidor': '3124445555',
            'nomenclatura': 'Calle 5 # 6-7',
            'barrio': 'El Centro',
            'municipio_id': self.muni.id,

            # Producto
            'producto_id': self.prod.id,
            'cantidad': '2'
        }
        response = self.client.post(reverse('admin_pedido_crear'), pedido_data)
        self.assertEqual(response.status_code, 302)
        
        # Verificar
        self.assertTrue(Pedido.objects.filter(cliente=self.cliente_user).exists())
        pedido = Pedido.objects.get(cliente=self.cliente_user)
        self.assertEqual(pedido.total, 20000.0)
        self.assertEqual(pedido.estado_pedido, self.estado_creado)
        self.assertEqual(pedido.detalles.count(), 1)
        self.assertEqual(pedido.detalles.first().cantidad, 2)
        self.assertEqual(pedido.direccion_cliente.nombre_recibidor, 'Carlos Recibe')
        
        # Verificar stock restado
        self.prod.refresh_from_db()
        self.assertEqual(self.prod.cantidad_stock, 8)

        # 3. GET editar formulario
        response = self.client.get(reverse('admin_pedido_editar', args=[pedido.id]))
        self.assertEqual(response.status_code, 200)

        # 4. POST editar pedido (cambiar estado a enviado, y total)
        edit_data = {
            'cliente_id': self.cliente_user.id,
            'estado_pedido_id': self.estado_enviado.id,
            'subtotal': '15000.00',
            'costo_envio': '7000.00',
            'total': '22000.00',
            
            'nombre_recibidor': 'Carlos Recibe Editado',
            'telefono_recibidor': '3124445555',
            'nomenclatura': 'Calle 5 # 6-7',
            'barrio': 'El Centro',
            'municipio_id': self.muni.id
        }
        response = self.client.post(reverse('admin_pedido_editar', args=[pedido.id]), edit_data)
        self.assertEqual(response.status_code, 302)
        
        pedido.refresh_from_db()
        self.assertEqual(pedido.estado_pedido, self.estado_enviado)
        self.assertEqual(pedido.total, 22000.0)
        self.assertEqual(pedido.direccion_cliente.nombre_recibidor, 'Carlos Recibe Editado')

        # 5. POST eliminar pedido
        response = self.client.post(reverse('admin_pedido_eliminar', args=[pedido.id]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Pedido.objects.filter(pk=pedido.id).exists())
