FROM python:3.11-slim

# Instala dependências do sistema
RUN apt-get update && \
    apt-get install -y ffmpeg && \
    rm -rf /var/lib/apt/lists/*

# Cria diretório de trabalho
WORKDIR /app

# Copia arquivos do projeto
COPY . /app

# Instala dependências Python
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Expõe porta padrão do FastAPI
EXPOSE 8000

# Comando para iniciar o servidor
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]