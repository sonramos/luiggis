# Luiggis (Django) — Desenvolvimento com Docker

Este repositório contém um projeto Django que roda com PostgreSQL via Docker Compose.
O objetivo deste README é orientar desenvolvedores (alunos) a configurar o ambiente local corretamente,
sem gerar arquivos com propriedade `root` no host.

## Passos iniciais

1. Copie o arquivo de exemplo de variáveis de ambiente:

```bash
cp .env.example .env
# Edite .env se desejar alterar SECRET_KEY, senhas, ou ALLOWED_HOSTS
```

2. Opcional: defina `USER_ID` e `GROUP_ID` no seu `.env` para combinar com seu usuário do host.
   Por exemplo (Linux/macOS):

```bash
# abra .env e altere USER_ID/GROUP_ID, ou execute:
printf "USER_ID=%s\nGROUP_ID=%s\n" "$(id -u)" "$(id -g)" >> .env
```

3. Build e up dos containers (recomendado passar IDs do host no build):

```bash
# Usando docker compose (passando build-args):
USER_ID=$(id -u) GROUP_ID=$(id -g) docker compose build --no-cache --progress=plain
docker compose up -d --build

# Alternativa (compose lerá USER_ID/GROUP_ID do .env):
# docker compose build --no-cache
# docker compose up -d
```

Observação: o `Dockerfile` cria um usuário `appuser` com UID/GID informados durante o build.
Quando `USER_ID`/`GROUP_ID` correspondem ao seu usuário no host, arquivos criados pelo container
no volume montado aparecerão com sua propriedade (evita arquivos `root`).

## Inicializar banco e criar superuser

Após o container `web` subir, rode as migrações e crie um superuser:

```bash
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser
```

## Notas sobre permissões

- Se você já tem arquivos no host que ficaram com `root` após execuções anteriores, corrija usando:

```bash
sudo chown -R $(id -u):$(id -g) .
```

- Para evitar problemas no futuro, certifique-se de sempre buildar com `USER_ID`/`GROUP_ID`
  iguais aos do seu usuário local (ou definir essas variáveis em `.env`).

## Comandos úteis

- Parar e remover containers:

```bash
docker compose down
```

- Ver logs do serviço web:

```bash
docker compose logs -f web
```

## Contribuição

- Mantenha as migrations no repositório para que todos possam reproduzir e sincronizar o esquema.
- Não commite o arquivo `.env` com segredos reais.
