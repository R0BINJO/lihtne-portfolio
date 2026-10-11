FROM python:3.14-slim AS base
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
RUN groupadd --gid 10001 portfolio && useradd --uid 10001 --gid 10001 --no-create-home portfolio
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY portfolio portfolio
COPY showcase showcase
COPY templates templates
COPY static static
COPY scripts scripts
COPY manage.py serve_admin.py serve_public.py ./
RUN mkdir -p private published staticfiles backups && chown -R 10001:10001 private published staticfiles backups
FROM base AS admin
USER 10001:10001
CMD ["sh", "scripts/container-admin.sh"]
FROM python:3.14-slim AS public
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PUBLIC_BIND=0.0.0.0
WORKDIR /app
RUN pip install --no-cache-dir waitress==3.0.2 whitenoise==6.12.0
COPY static static
COPY serve_public.py .
USER 10002:10002
CMD ["python", "serve_public.py"]
