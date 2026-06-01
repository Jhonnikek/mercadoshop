## MercadoShop


## Tecnologías

* **Django:** Framework web principal.
* **uv:** Gestor de paquetes de Python
* **Docker & Docker Compose:** Contenerización del proyecto con entornos separados para desarrollo y producción.

## Gestión de Dependencias (Local)

1. Instala las dependencias declaradas en el `pyproject.toml` y el `uv.lock`. Esto creará el entorno virtual `.venv` automáticamente:
```bash
uv sync mecardoshop
```

2. Para agregar deps:
```bash
uv add <nombre_del_paquete>
```

3. contenedor de desarrollo:
```bash
docker compose -f compose.dev.yml up --build
```