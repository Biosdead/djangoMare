# Python base image
FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    APP_HOME=/app

WORKDIR ${APP_HOME}

# System deps
RUN apt-get update -y && apt-get install -y --no-install-recommends \
    build-essential \
  && rm -rf /var/lib/apt/lists/*

# Copy requirements first for caching
COPY requirements.txt ./
RUN pip install -r requirements.txt

# Copy project
COPY . .

# Static collection
ENV DJANGO_DEBUG=False
RUN python mare/manage.py collectstatic --noinput || true

# Expose and run
EXPOSE 8000
CMD ["gunicorn", "mare.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]

