# Imagen base de Python
FROM python:3.13-slim

# Evita que Python escriba archivos .pyc
ENV PYTHONDONTWRITEBYTECODE=1

# Muestra los logs en la consola
ENV PYTHONUNBUFFERED=1

# Carpeta de trabajo dentro del contenedor
WORKDIR /app

# Copia primero requirements para aprovechar el cache de Dockerç
COPY requirements.txt .

# Instala las dependencias del proyecto
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto del código de la aplicación
COPY . .

# Crea la carpeta para los archivos estáticos para que WhiteNoise pueda servirlos
RUN python manage.py collectstatic --noinput

# Puerto interno de Django
EXPOSE 8000

# Aplica las migraciones y luego inicia el servidor de desarrollo con gunicorn
CMD ["sh", "-c", "python manage.py migrate --noinput && gunicorn minierp.wsgi:application --bind 0.0.0.0:8000"]