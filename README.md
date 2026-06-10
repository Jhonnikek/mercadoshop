# MercadoShop

Proyecto híbrido con backend Django y app móvil Flutter.

## Estructura

- `app/`: backend Django con REST API para clientes y panel de administración.
- `androidapp/`: aplicación Flutter que consume la API del backend.
- `compose.dev.yml`, `compose.yml`: Docker Compose para desarrollo y producción.
- `pyproject.toml`: dependencias Python/Django.
- `androidapp/pubspec.yaml`: dependencias Flutter.

## Tecnologías

- Backend: Django, Django REST Framework, MySQL
- Móvil: Flutter, Dio, Riverpod, GoRouter, flutter_dotenv

## Ejecución

1. Instalar dependencias backend:
   ```bash
   uv sync mecardoshop

2. Levantar backend en desarrollo:
   ```bash
   docker compose -f compose.dev.yml up --build
   ```
3. Ejecutar la app Flutter:
   ```bash
   cd androidapp
   flutter pub get
   flutter run
   ```
4. Configuración de la app:
   
   - Usa .env en androidapp/ para BASE_URL.
   
   - En emulador Android, el valor por defecto es http://10.0.2.2:8000.   