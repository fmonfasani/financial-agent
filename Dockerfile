# Dockerfile
FROM python:3.10-slim

# 1. Crea el directorio de trabajo
WORKDIR /workspace

# 2. Copia sólo requirements primero para cachear pip install
COPY requirements.txt .

# 3. Instala dependencias
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copia el resto del código
COPY . .

# 5. Punto de entrada por defecto
CMD ["bash", "-c", "python agent/slackbot.py"]
