ARG PYTHON_VERSION=3.12.3
FROM python:${PYTHON_VERSION}-slim as base
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1         
ENV PIPENV_VENV_IN_PROJECT=1 

WORKDIR /app

# Instalações necessárias para o Python e Node.js
RUN apt-get update && apt-get install -y \
    build-essential \
    libmariadb-dev-compat \
    libmariadb-dev \
    pkg-config \
    curl \
    && curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && pip install --no-cache-dir pipenv \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Instala dependências Python
COPY Pipfile Pipfile.lock /app/
RUN pipenv install --deploy --system

# Instala dependências Node.js
COPY package.json /app/
COPY package-lock.json /app/
RUN npm install

# Copia o restante do projeto
COPY . /app/

# Gera os arquivos estáticos
# RUN npx grunt build

# Comando padrão
CMD ["python", "manage.py", "runserver", "0.0.0.0:8001"]