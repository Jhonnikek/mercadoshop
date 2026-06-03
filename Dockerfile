FROM python:3.12-slim

RUN apt-get update && apt-get install -y libpq-dev && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:0.10.4 /uv /uvx /bin/

WORKDIR /code

COPY pyproject.toml uv.lock ./

RUN uv sync --frozen --no-cache

COPY ./app ./app

EXPOSE 80

CMD ["uv", "run", "gunicorn", "--chdir", "app", "config.wsgi:application", "--bind", "0.0.0.0:80"]
