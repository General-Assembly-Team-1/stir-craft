# ==============================================================================
# StirCraft Django Application Dockerfile
# ==============================================================================
# This Dockerfile creates a production-ready container for the StirCraft Django app.
# It uses a multi-stage build to keep the final image size small and secure.
#
# Build stages:
# 1. base: Sets up Python environment and system dependencies
# 2. dependencies: Installs Python packages using pipenv
# 3. production: Final lightweight image with just the app and runtime deps
#
# Usage:
#   docker build -t stircraft:latest .
#   docker run -p 8000:8000 stircraft:latest
# ==============================================================================

# ------------------------------------------------------------------------------
# Stage 1: Base Python environment with system dependencies
# ------------------------------------------------------------------------------
# Use Python 3.11 slim image as base - smaller than full Python image
FROM python:3.11-slim as base

# Set environment variables for Python optimization
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies needed for Django and PostgreSQL
# - postgresql-client: for connecting to PostgreSQL database
# - build-essential: for compiling Python packages with C extensions
# - libpq-dev: PostgreSQL development headers for psycopg2
# - gettext: for Django internationalization support
RUN apt-get update && apt-get install -y \
    postgresql-client \
    build-essential \
    libpq-dev \
    gettext \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
# Running as root inside containers is a security risk
RUN useradd --create-home --shell /bin/bash stircraft

# Set working directory where the app will live
WORKDIR /app

# Change ownership of /app to our non-root user
RUN chown stircraft:stircraft /app

# ------------------------------------------------------------------------------
# Stage 2: Install Python dependencies
# ------------------------------------------------------------------------------
FROM base as dependencies

# Install pipenv for dependency management
RUN pip install pipenv

# Copy dependency files first (for Docker layer caching)
# This allows Docker to cache the dependency installation step
# if only source code changes, not dependencies
COPY Pipfile Pipfile.lock ./

# Install Python dependencies from Pipfile
# --system: Install packages to system Python instead of virtual environment
# --deploy: Only install exact versions from Pipfile.lock (production mode)
# --ignore-pipfile: Use Pipfile.lock only, ignore Pipfile
RUN pipenv install --system --deploy --ignore-pipfile

# ------------------------------------------------------------------------------
# Stage 3: Production image with application code
# ------------------------------------------------------------------------------
FROM base as production

# Copy installed packages from dependencies stage
COPY --from=dependencies /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=dependencies /usr/local/bin /usr/local/bin

# Switch to non-root user
USER stircraft

# Copy application code
# .dockerignore file should exclude unnecessary files
COPY --chown=stircraft:stircraft . .

# Create directories for static files and media uploads
RUN mkdir -p stircraft/stir_craft/staticfiles stircraft/stir_craft/media

# Set environment variables for Django
ENV DJANGO_SETTINGS_MODULE=stircraft.settings \
    PYTHONPATH=/app

# Expose port 8000 (Django's default development port)
# In production, you might use a different port or proxy through nginx
EXPOSE 8000

# Health check to ensure the container is running properly
# This tells Docker/orchestration systems if the app is healthy
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python stircraft/manage.py check --deploy || exit 1

# Default command to run the application
# Uses Gunicorn as the WSGI server for production
# - --bind 0.0.0.0:8000: Listen on all interfaces, port 8000
# - --workers 4: Number of worker processes (adjust based on CPU cores)
# - --timeout 120: Request timeout in seconds
# - --max-requests 1000: Restart workers after handling this many requests
# - --max-requests-jitter 100: Add randomness to max-requests to avoid thundering herd
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "--timeout", "120", "--max-requests", "1000", "--max-requests-jitter", "100", "stircraft.wsgi:application"]
