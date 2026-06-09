# MercadoShop Desktop

Aplicación de escritorio desarrollada en Flutter para la administración de inventario y visualización de métricas de MercadoShop. Está diseñada específicamente con un sistema de diseño premium (Dark Mode) enfocado en la experiencia de usuario y la eficiencia administrativa.

## 🚀 Características

- **Autenticación Segura**: Inicio y cierre de sesión con manejo de tokens JWT (Access y Refresh).
- **Dashboard Interactivo**: 
  - Visualización en tiempo real de métricas importantes (Total de productos, Mayor stock, Producto más caro).
  - Listado rápido de los últimos productos añadidos.
  - Sidebar con información de la tienda y el usuario autenticado.
- **Gestión de Inventario (CRUD)**:
  - Listado completo de productos con paginación y búsqueda en tiempo real.
  - Creación de nuevos productos.
  - Edición de productos existentes.
  - Eliminación con validación de seguridad.
- **Sistema de Diseño Consistente**: Interfaz completamente estandarizada usando `AppTheme` con paletas de colores índigo oscuro, tipografía `Inter` y componentes visuales uniformes.

## 🛠 Tecnologías Utilizadas

- **Framework**: [Flutter](https://flutter.dev/) (Optimizado para Windows/Desktop)
- **Lenguaje**: Dart
- **Manejo de Estado**: `provider`
- **Enrutamiento**: `go_router`
- **Almacenamiento Seguro**: `flutter_secure_storage` (para tokens y datos de sesión)
- **Peticiones HTTP**: Paquete `http` para comunicación con la API REST.
- **Tipografía**: `google_fonts` (Inter)

## 📋 Requisitos Previos

Asegúrate de tener instalado:
- Flutter SDK (versión 3.0 o superior recomendada).
- Habilitado el desarrollo para escritorio (`flutter config --enable-windows-desktop`).
- Un IDE compatible (VS Code, Android Studio, IntelliJ).

## ⚙️ Instalación y Ejecución

1. Clona este repositorio o descarga el código fuente.
2. Abre una terminal en la raíz del proyecto.
3. Descarga las dependencias ejecutando:
   ```bash
   flutter pub get
   ```
4. Ejecuta la aplicación en modo escritorio (Windows):
   ```bash
   flutter run -d windows
   ```

## 🏗 Estructura del Proyecto

El proyecto sigue una estructura limpia separada por responsabilidades:

- `lib/core/`: Constantes y el sistema de diseño (`theme.dart`).
- `lib/models/`: Modelos de datos (ej. `producto.dart`).
- `lib/providers/`: Lógica de estado y conexión con la UI (`auth_provider.dart`, `producto_provider.dart`).
- `lib/services/`: Lógica pura de peticiones HTTP a la API REST.
- `lib/screens/`: Pantallas de la interfaz organizadas por módulos (Login, Dashboard).
