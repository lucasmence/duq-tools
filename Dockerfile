# Dockerfile
FROM python:3.11-slim
WORKDIR /app

# Copia todos os arquivos locais do diretório atual para dentro da imagem
COPY . /app

# O comando roda os servidores em background (&) e o último em foreground para manter o container vivo
CMD sh -c "python -m http.server --directory duq-sprite-editor 8081 & python -m http.server --directory duq-sprite-fusion 8082 & exec python -m http.server --directory duq-trigger-editor 8083"
