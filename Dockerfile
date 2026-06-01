FROM python:3.12-slim-bookworm
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Copy dependency definition files
COPY pyproject.toml uv.lock ./

# Install project dependencies
RUN uv sync --frozen --no-cache

# Copy the rest of the application
COPY . .

# Expose Django port
EXPOSE 8000

# Set environment variables to run using uv environment
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

CMD ["python", "app/manage.py", "runserver", "0.0.0.0:8000"]
