FROM python:3.12

# Build arguments to set container user UID/GID to match host user.
ARG USER_ID=1000
ARG GROUP_ID=1000

# Evita arquivos .pyc e usa stdout sem buffer
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Cria grupo/usuário com UID/GID passados para evitar arquivos root no host
RUN groupadd -g ${GROUP_ID} appgroup || true \
	&& useradd -m -u ${USER_ID} -g ${GROUP_ID} -s /bin/bash appuser || true

WORKDIR /usr/src/app

# Copia requirements com ownership para o usuário criado e instala dependências
COPY --chown=appuser:appgroup requirements.txt /usr/src/app/
RUN pip install --no-cache-dir -r requirements.txt

# Copia o restante do projeto com ownership para o usuário criado
COPY --chown=appuser:appgroup . /usr/src/app/

# Executa o container como o usuário não-root (mesmo UID do host quando informado)
USER appuser

