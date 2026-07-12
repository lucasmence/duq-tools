# Dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . /app
CMD ["sh", "-c", "python -m http.server --directory duq-sprite-editor 8081 & python -m http.server --directory duq-sprite-fusion 8082 & python -m http.server --directory duq-trigger-editor 8083"]
