import os
import django

# Cargar configuración de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import (
    Usuario, Departamento, Municipio, Direccion, EstadoPedido, Rol, Categoria,
    Tienda, Producto, TrabajadorTienda, Pedido, DetallePedido, DireccionCliente
)

def crear_datos():
    print("Inicializando datos de prueba en la base de datos...")
    
    # 1. Crear Departamento
    depto, _ = Departamento.objects.get_or_create(nombre="Antioquia", codigo_dane="05")
    
    # 2. Crear Municipio
    muni, _ = Municipio.objects.get_or_create(departamento=depto, nombre="Medellín", codigo_dane="05001")
    
    # 3. Crear Direcciones
    dir_tienda_a, _ = Direccion.objects.get_or_create(nomenclatura="Calle 10 # 43-21", barrio="El Poblado", municipio=muni)
    dir_tienda_b, _ = Direccion.objects.get_or_create(nomenclatura="Carrera 80 # 35-12", barrio="Laureles", municipio=muni)
    dir_cliente, _ = Direccion.objects.get_or_create(nomenclatura="Circular 4 # 72-10", barrio="Conquistadores", municipio=muni)
    
    # 4. Crear Estado de Pedido
    estado_creado, _ = EstadoPedido.objects.get_or_create(nombre_estado="Creado")
    estado_entregado, _ = EstadoPedido.objects.get_or_create(nombre_estado="Entregado")
    
    # 5. Crear Rol de Trabajador
    rol_cajero, _ = Rol.objects.get_or_create(nombre="Cajero", descripcion="Registra ventas y atiende pedidos")
    
    # 6. Crear Categorías
    cat_tecnologia, _ = Categoria.objects.get_or_create(nombre_categoria="Tecnología", estado=True)
    cat_moda, _ = Categoria.objects.get_or_create(nombre_categoria="Moda", estado=True)
    cat_hogar, _ = Categoria.objects.get_or_create(nombre_categoria="Hogar y Decoración", estado=True)
    cat_belleza, _ = Categoria.objects.get_or_create(nombre_categoria="Belleza y Cuidado Personal", estado=True)
    cat_ferreteria, _ = Categoria.objects.get_or_create(nombre_categoria="Ferretería y Construcción", estado=True)
    cat_alimentos, _ = Categoria.objects.get_or_create(nombre_categoria="Alimentos y Bebidas", estado=True)
    cat_papeleria, _ = Categoria.objects.get_or_create(nombre_categoria="Papelería y Oficina", estado=True)
    cat_deportes, _ = Categoria.objects.get_or_create(nombre_categoria="Deportes y Bienestar", estado=True)
    cat_servicios, _ = Categoria.objects.get_or_create(nombre_categoria="Servicios Empresariales", estado=True)
    cat_mascotas, _ = Categoria.objects.get_or_create(nombre_categoria="Mascotas", estado=True)
    
    # 7. Crear Tiendas
    tienda_a, _ = Tienda.objects.get_or_create(
        nombre_comercial="ElectroShop",
        descripcion="Todo en tecnología, computadores y celulares",
        correo_atencion="contacto@electroshop.com",
        telefono_atencion="1234567",
        razon_social="ElectroShop S.A.S",
        direccion=dir_tienda_a,
        estado_tienda="Activa"
    )
    
    tienda_b, _ = Tienda.objects.get_or_create(
        nombre_comercial="ModaExpress",
        descripcion="Ropa casual y accesorios",
        correo_atencion="info@modaexpress.com",
        telefono_atencion="7654321",
        razon_social="ModaExpress S.A.S",
        direccion=dir_tienda_b,
        estado_tienda="Activa"
    )
    
    # 8. Crear Usuarios
    # Admin (Superusuario)
    if not Usuario.objects.filter(username="admin").exists():
        Usuario.objects.create_superuser("admin", "admin@mercadoshop.com", "adminpass", tipo_usuario="ADMIN")
        print("- Admin creado (admin / adminpass)")
        
    # Cliente
    cliente, created = Usuario.objects.get_or_create(
        username="cliente_test",
        email="cliente@correo.com",
        tipo_usuario="CLIENTE",
        direccion_principal=dir_cliente,
        telefono="3001234567"
    )
    if created:
        cliente.set_password("clientepass")
        cliente.save()
        print("- Cliente de prueba creado (cliente_test / clientepass)")
        
    # DireccionCliente para el cliente
    dir_cliente_envio, _ = DireccionCliente.objects.get_or_create(
        cliente=cliente,
        direccion=dir_cliente,
        etiqueta="Casa",
        nombre_recibidor="Pepito Perez",
        telefono_recibidor="3001234567"
    )
        
    # Trabajador A (ElectroShop)
    trabajador_a, created = Usuario.objects.get_or_create(
        username="trabajador_electro",
        email="trabajador_a@correo.com",
        tipo_usuario="TRABAJADOR",
        rol_trabajador=rol_cajero
    )
    if created:
        trabajador_a.set_password("trabajadorpass")
        trabajador_a.save()
        print("- Trabajador A creado (trabajador_electro / trabajadorpass)")
        
    # Trabajador B (ModaExpress)
    trabajador_b, created = Usuario.objects.get_or_create(
        username="trabajador_moda",
        email="trabajador_b@correo.com",
        tipo_usuario="TRABAJADOR",
        rol_trabajador=rol_cajero
    )
    if created:
        trabajador_b.set_password("trabajadorpass")
        trabajador_b.save()
        print("- Trabajador B creado (trabajador_moda / trabajadorpass)")
        
    # 9. Vincular Trabajadores a Tiendas
    TrabajadorTienda.objects.get_or_create(tienda=tienda_a, trabajador=trabajador_a)
    TrabajadorTienda.objects.get_or_create(tienda=tienda_b, trabajador=trabajador_b)

    tienda_a.categorias.set([cat_tecnologia, cat_hogar, cat_servicios])
    tienda_b.categorias.set([cat_moda, cat_belleza, cat_deportes])
    
    # 10. Crear Productos
    prod_celular, _ = Producto.objects.get_or_create(
        tienda=tienda_a,
        descripcion_corta="Celular Smart X",
        descripcion_larga="Pantalla OLED 6.7 pulgadas, 128GB",
        categoria=cat_tecnologia,
        precio_unitario=1500000.0000,
        cantidad_stock=10
    )
    
    prod_camisa, _ = Producto.objects.get_or_create(
        tienda=tienda_b,
        descripcion_corta="Camisa Slim Fit",
        descripcion_larga="Algodón 100% color azul",
        categoria=cat_moda,
        precio_unitario=89900.0000,
        cantidad_stock=25
    )

    if not Producto.objects.filter(tienda=tienda_a, descripcion_corta="Portátil Business Pro").exists():
        Producto.objects.create(
            tienda=tienda_a,
            descripcion_corta="Portátil Business Pro",
            descripcion_larga="Equipo para oficinas y trabajo híbrido",
            categoria=cat_tecnologia,
            precio_unitario=3200000.0000,
            cantidad_stock=8,
        )

    if not Producto.objects.filter(tienda=tienda_a, descripcion_corta="Kit Oficina Premium").exists():
        Producto.objects.create(
            tienda=tienda_a,
            descripcion_corta="Kit Oficina Premium",
            descripcion_larga="Escritorio compacto, lámpara y accesorios",
            categoria=cat_papeleria,
            precio_unitario=180000.0000,
            cantidad_stock=15,
        )

    if not Producto.objects.filter(tienda=tienda_b, descripcion_corta="Cafetera Compacta").exists():
        Producto.objects.create(
            tienda=tienda_b,
            descripcion_corta="Cafetera Compacta",
            descripcion_larga="Ideal para cocinas pequeñas y oficinas",
            categoria=cat_hogar,
            precio_unitario=220000.0000,
            cantidad_stock=12,
        )

    if not Producto.objects.filter(tienda=tienda_b, descripcion_corta="Kit Fitness Basic").exists():
        Producto.objects.create(
            tienda=tienda_b,
            descripcion_corta="Kit Fitness Basic",
            descripcion_larga="Bandas, botella y accesorios para entrenamiento",
            categoria=cat_deportes,
            precio_unitario=99000.0000,
            cantidad_stock=30,
        )

    cliente.categorias_interes.set([cat_tecnologia, cat_hogar, cat_servicios])
    trabajador_a.categorias_interes.set([cat_tecnologia, cat_ferreteria])
    trabajador_b.categorias_interes.set([cat_moda, cat_belleza, cat_deportes])
    
    # 11. Crear Pedidos
    # Pedido 1: Para ElectroShop (contiene Celular Smart X)
    pedido_1, created = Pedido.objects.update_or_create(
        numero_comprobante="COMP-001",
        defaults={
            "cliente": cliente,
            "direccion_cliente": dir_cliente_envio,
            "subtotal": 1500000.0000,
            "costo_envio": 10000.0000,
            "total": 1510000.0000,
            "estado_pedido": estado_creado,
        },
    )
    if created:
        DetallePedido.objects.get_or_create(
            pedido=pedido_1,
            producto=prod_celular,
            nombre_producto=prod_celular.descripcion_corta,
            precio_compra=prod_celular.precio_unitario,
            cantidad=1,
            subtotal=prod_celular.precio_unitario
        )
        
    # Pedido 2: Para ModaExpress (contiene Camisa Slim Fit)
    pedido_2, created = Pedido.objects.update_or_create(
        numero_comprobante="COMP-002",
        defaults={
            "cliente": cliente,
            "direccion_cliente": dir_cliente_envio,
            "subtotal": 89900.0000,
            "costo_envio": 8000.0000,
            "total": 97900.0000,
            "estado_pedido": estado_creado,
        },
    )
    if created:
        DetallePedido.objects.get_or_create(
            pedido=pedido_2,
            producto=prod_camisa,
            nombre_producto=prod_camisa.descripcion_corta,
            precio_compra=prod_camisa.precio_unitario,
            cantidad=1,
            subtotal=prod_camisa.precio_unitario
        )

    print("Inicialización completa. Todos los datos de prueba han sido cargados con éxito.")

if __name__ == "__main__":
    crear_datos()
