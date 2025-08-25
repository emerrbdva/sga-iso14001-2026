# Usa una imagen base oficial de Python
FROM python:3.11-slim

# Instalar curl para que el healthcheck funcione
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Establece el directorio de trabajo en /app
WORKDIR /app

# Instala el paquete de modelos compartidos
COPY shared_models /app/shared_models
RUN pip install ./shared_models

# Copia los archivos de la aplicación
COPY services/reporting_engine/requirements.txt /app/
COPY services/reporting_engine/main.py /app/
COPY services/reporting_engine/app /app/app

# Instala las dependencias
RUN pip install --no-cache-dir --timeout=600 -r requirements.txt

# Expone el puerto del servicio de reportes
EXPOSE 8007

# Comando para correr la aplicación
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8007"]