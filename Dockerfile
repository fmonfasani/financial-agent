# Dockerfile
FROM python:3.10-slim
WORKDIR /workspace
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["bash","-c","python app.py"]
