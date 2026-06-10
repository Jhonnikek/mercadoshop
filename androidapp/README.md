# MercadoShop - App Android (Flutter)

Este repositorio contiene la aplicación móvil de MercadoShop (desarrollada en Flutter) junto con el backend Django y la infraestructura para desarrollo.

## Descripción

MercadoShop es una aplicación de ejemplo que muestra una tienda de productos con listados de productos y tiendas. La aplicación móvil consume una API REST (Django + Django REST Framework) incluida en este mismo repositorio.

## Estado del proyecto

- Lenguaje frontend: Dart (Flutter)
- Backend: Python (Django, Django REST Framework)
- Contenedores y desarrollo: Docker / Docker Compose

## Estructura principal del repositorio

- `androidapp/`: Aplicación Flutter (cliente móvil)
	- `lib/`: Código fuente de la app Flutter
	- `pubspec.yaml`: Dependencias y configuración de Flutter
	- `.env` (no incluida): Variables de entorno usadas por la app
- `app/`: Proyecto Django (backend)
- `compose.dev.yml`, `compose.yml`, `Dockerfile`: Configuración para Docker Compose
- `pyproject.toml`: Dependencias del backend
- `LICENSE`: Licencia del proyecto

## Tecnologías

- Flutter (Dart)
- Flutter Riverpod, Dio, go_router, flutter_dotenv
- Django, Django REST Framework, SimpleJWT
- Docker, Docker Compose

## Requisitos

- Flutter SDK (compatible con la versión indicada en `pubspec.yaml`)
- Android SDK / emulador o dispositivo físico
- Python 3.12+ (para el backend si se ejecuta localmente)
- Docker & Docker Compose (opcional, recomendado para desarrollo)

## Configuración y ejecución

Hay dos formas recomendadas de ejecutar el sistema: con Docker Compose (más sencillo y reproducible) o ejecutando el backend y la app localmente.

### Opción A — Usar Docker Compose (recomendado para desarrollo)

1. Desde la raíz del repositorio, levantar los servicios:

```bash
docker compose -f compose.dev.yml up --build
```

2. Esto construye y arranca el backend y servicios necesarios. Asegúrate de revisar los ficheros `compose.dev.yml` y `compose.yml` para variables y puertos.

3. Para ejecutar la app Flutter en modo desarrollo, abre otra terminal, ve a `androidapp/` y ejecuta:

```bash
cd androidapp
flutter pub get
flutter run
```

Nota: Si usas un emulador Android, la URL por defecto del backend en la app es `http://10.0.2.2:8000` (configurada en `ApiConstants`).

### Opción B — Ejecutar backend y app localmente

Backend (localmente):

1. Crear y activar un entorno virtual Python:

```bash
python -m venv .venv
.venv\Scripts\activate   # Windows
source .venv/bin/activate # macOS / Linux
```

2. Instalar dependencias (se listan en `pyproject.toml`):

```bash
pip install -U pip
pip install django djangorestframework djangorestframework-simplejwt django-environ gunicorn mysqlclient
```

3. Ir a la carpeta del proyecto Django y ejecutar las migraciones:

```bash
cd app
python manage.py migrate
python manage.py runserver
```

4. Ejecuta pruebas unitarias (si aplica):

```bash
python manage.py test
```

Frontend (Flutter):

1. Crear el archivo `.env` en `androidapp/` (no se sube al repositorio). Al menos debe contener la variable `BASE_URL` que apunta a la API. Ejemplos:

- Para emulador Android (con backend en localhost):



```
BASE_URL=http://10.0.2.2:8000
```

- Para dispositivo físico o backend remoto:

```
BASE_URL=https://api.mi-servidor.com
```

2. Instalar dependencias y ejecutar la app:

```bash
cd androidapp
flutter pub get
flutter run
```

## Variables de entorno importantes

- `BASE_URL`: URL base de la API REST. Por defecto, en la app se usa `http://10.0.2.2:8000` si no se define.

## Endpoints principales (ejemplos)

- Listar productos: `GET /api/clientes/productos/`
- Listar tiendas: `GET /api/clientes/tiendas/`

Estos endpoints están definidos en el backend (ver `app/tiendas/` y `app/clientes/`).

## Desarrollo y pruebas

- Flutter: usa `flutter test` y `flutter analyze` para pruebas y análisis estático.
- Backend: usa `python manage.py test`.

## Contribuir

1. Haz fork del repositorio.
2. Crea una rama descriptiva: `feature/mi-cambio`.
3. Abre un Pull Request con descripción del cambio.

Por favor, mantén el mismo estilo y linters del proyecto.

## Licencia

Este proyecto está bajo la licencia indicada en [LICENSE](../LICENSE).

## Contacto

Para dudas o propuestas, abre un issue en este repositorio.

---

Si quieres, adapto o amplío alguna sección con más detalle (por ejemplo: instrucciones completas de despliegue en producción, variables de entorno del backend o ejemplos de uso de la API). 
