# Dockerfile
FROM ghcr.io/tu_usuario/financial-agent-base:latest
WORKDIR /workspace
COPY . .
CMD ["bash","-c","python app.py"]