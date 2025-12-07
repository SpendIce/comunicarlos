# Dockerfile multi-stage para optimizar el tamaño de la imagen

# Etapa 1: Builder
FROM python:3.11-slim as builder

WORKDIR /app

# Instalar dependencias del sistema necesarias para compilar
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copiar archivos de dependencias
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir --user -r requirements.txt

# Etapa 2: Runtime
FROM python:3.11-slim

WORKDIR /app

# Copiar dependencias instaladas desde builder
COPY --from=builder /root/.local /root/.local

# Asegurar que los scripts de usuario estén en el PATH
ENV PATH=/root/.local/bin:$PATH

# Copiar código de la aplicación
COPY ./app /app/app
COPY ./app/main.py /app/main.py

# Exponer puerto
EXPOSE 8080

# Variables de entorno
ENV PYTHONUNBUFFERED=1
ENV MONGODB_URL=mongodb://mongodb:27017

# Comando para ejecutar la aplicación
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]