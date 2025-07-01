FROM python:3.10-slim

# Instalar Tesseract e dependências básicas
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    poppler-utils \
    && apt-get clean

# Criar diretório do app
WORKDIR /app

# Copiar arquivos do projeto
COPY . .

# Instalar as dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Expõe a porta do Gunicorn
EXPOSE 10000

# Rodar o app com Gunicorn
CMD ["gunicorn", "-b", "0.0.0.0:10000", "app:app"]
