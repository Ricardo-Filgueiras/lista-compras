# Arquitetura Oficial — Django + UV + Docker + GitHub + EasyPanel

Este guia define **estrutura obrigatória** para:

- 🔹 Desenvolvimento local isolado
- 🔹 Build determinístico com UV
- 🔹 Produção via Docker
- 🔹 Deploy automatizado no EasyPanel
- 🔹 Separação absoluta entre DEV e PRODUÇÃO

---

# 📁 Estrutura do Projeto


```
project/
│
├── pyproject.toml
├── uv.lock
├── Dockerfile
├── docker-compose.yml
│
├── dotenv_files/
│    └── .env.example
│
├── scripts/
│   ├── commands.sh
│   ├── wait_psql.sh
│   ├── entrypoint_prod.sh
│   └── start_gunicorn.sh
│
└── app/ # (src)
└── manage.py

```

---

# 🔵 AMBIENTE 1 — DESENVOLVIMENTO LOCAL

## 🎯 Objetivo

- Iteração rápida
- Hot reload
- Permitir makemigrations
- Uso de runserver
- Banco local via docker-compose

---

## 1️⃣ docker-compose.yml (DEV)

Responsável por:

- Subir Django
- Subir Postgres 15
- Montar volumes
- Executar commands.sh

Exemplo:

```yaml
version: "3.9"

services:
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: devdb
      POSTGRES_USER: devuser
      POSTGRES_PASSWORD: devpass
    volumes:
      - postgres_dev_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  web:
    build: .
    command: ["sh", "scripts/commands.sh"]
    volumes:
      - ./app:/app
    env_file:
      - dotenv_files/.env.dev
    ports:
      - "8000:8000"
    depends_on:
      - db

volumes:
  postgres_dev_data:

```
---
#
2️⃣ scripts/commands.sh (DEV)

Ordem típica:
```bash
#!/bin/sh

./scripts/wait_psql.sh
python manage.py makemigrations
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```

✔ Permitido no DEV:
- runserver
- makemigrations
- DEBUG=1

3️⃣ Variáveis DEV

Arquivo: 
```
dotenv_files/.env.dev

```

```
DEBUG=1
SECRET_KEY=dev-secret
POSTGRES_HOST=db
POSTGRES_PORT=5432
POSTGRES_DB=devdb
POSTGRES_USER=devuser
POSTGRES_PASSWORD=devpass
```

# 🔴 AMBIENTE 2 — PRODUÇÃO (EasyPanel)

## Objetivo
- Build determinístico
- Segurança
- Zero dependência de docker-compose
- Uso exclusivo de Gunicorn
- Banco como serviço separado

1️⃣ Dockerfile (PRODUÇÃO)

```Dockerfile
FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install uv

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

COPY . .

RUN chmod +x scripts/*.sh

EXPOSE 8000

CMD ["./scripts/entrypoint_prod.sh"]
```

2️⃣ scripts/entrypoint_prod.sh (PROD)
```bash
#!/bin/sh

./scripts/wait_psql.sh

python manage.py collectstatic --noinput
python manage.py migrate --noinput

./scripts/start_gunicorn.sh
```

3️⃣ scripts/start_gunicorn.sh (PROD)
```bash
#!/bin/sh

exec gunicorn app.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 3
```

🚫 Regras Absolutas de Produção

Produção NÃO pode:

- Usar runserver
- Executar makemigrations
- Depender de docker-compose
- Ter DEBUG=1
- Rodar sem uv.lock
- Rodar sem gunicorn

Se qualquer item acima ocorrer → deploy inválido.

🟣 Gerenciamento de Dependências (UV)
pyproject.toml (Produção mínima)
```toml
[project]
dependencies = [
    "django>=4.2,<5",
    "gunicorn>=21,<22",
    "psycopg[binary]"
]
```

Regras críticas:
- uv.lock deve estar versionado
- Docker deve usar uv sync --frozen
- Não usar requirements.txt em produção

🟢 EasyPanel — Configuração de Produção
1️⃣ Criar Postgres Service
Postgres 15
Volume habilitado
Copiar credenciais
2️⃣ Criar App Service

Configuração:

Source: GitHub
Branch: main
Builder: Dockerfile
Proxy Port: 8000
HTTPS habilitado
Auto Deploy ativado
3️⃣ Variáveis de Ambiente (Painel)

Obrigatórias:
```
DEBUG=0
SECRET_KEY=...
ALLOWED_HOSTS=seudominio.com

POSTGRES_HOST=
POSTGRES_PORT=5432
POSTGRES_DB=
POSTGRES_USER=
POSTGRES_PASSWORD=
``` 

### 📌 Comparação Final — DEV vs PRODUÇÃO
| Item           | DEV      | PRODUÇÃO    |
| -------------- | -------- | ----------- |
| runserver      | ✔        | ❌           |
| gunicorn       | ❌        | ✔           |
| makemigrations | ✔        | ❌           |
| DEBUG=1        | ✔        | ❌           |
| docker-compose | ✔        | ❌           |
| EasyPanel      | ❌        | ✔           |
| uv --frozen    | Opcional | Obrigatório |
| Postgres local | ✔        | ❌           |


# Comparação Final — DEV vs PRODUÇÃO

---

# ✅ CHECKLIST FINAL DE VALIDAÇÃO — PRONTO PARA PRODUÇÃO

Use esta seção antes de considerar o deploy como concluído.

---

## 🔎 1️⃣ Estrutura do Projeto

- [ ] `uv.lock` está versionado no repositório
- [ ] `pyproject.toml` está correto e sem dependências de DEV em produção
- [ ] `Dockerfile` usa `uv sync --frozen --no-dev`
- [ ] `Dockerfile` instala `postgresql-client`
- [ ] `Dockerfile` expõe a porta `8000`
- [ ] Scripts possuem permissão de execução (`chmod +x`)
- [ ] Nenhum `requirements.txt` sendo usado em produção

---

## 🔵 2️⃣ Ambiente de Desenvolvimento (Local)

- [ ] `docker-compose.yml` sobe Django + Postgres corretamente
- [ ] `commands.sh` executa:
  - [ ] wait_psql.sh
  - [ ] makemigrations
  - [ ] migrate
  - [ ] runserver
- [ ] `DEBUG=1` somente no `.env.dev`
- [ ] Volume de banco persistente
- [ ] Aplicação acessível em `localhost:8000`

---

## 🔴 3️⃣ Ambiente de Produção

- [ ] Produção NÃO usa `runserver`
- [ ] Produção NÃO executa `makemigrations`
- [ ] `entrypoint_prod.sh` executa na ordem correta:
  - [ ] wait_psql.sh
  - [ ] collectstatic --noinput
  - [ ] migrate --noinput
  - [ ] start_gunicorn.sh
- [ ] `start_gunicorn.sh` usa `gunicorn`
- [ ] `DEBUG=0`
- [ ] `ALLOWED_HOSTS` configurado corretamente

---

## 🟢 4️⃣ Configuração no EasyPanel

- [ ] Projeto criado
- [ ] Postgres Service criado
- [ ] Volume do Postgres ativo
- [ ] Credenciais copiadas corretamente
- [ ] App Service conectado ao GitHub
- [ ] Branch correta (ex: main)
- [ ] Builder configurado para Dockerfile
- [ ] Proxy configurado para porta 8000
- [ ] HTTPS habilitado
- [ ] Auto Deploy ativado

---

## 🟡 5️⃣ Variáveis de Ambiente

- [ ] `SECRET_KEY` definido
- [ ] `POSTGRES_HOST` correto
- [ ] `POSTGRES_PORT=5432`
- [ ] `POSTGRES_DB` correto
- [ ] `POSTGRES_USER` correto
- [ ] `POSTGRES_PASSWORD` correto
- [ ] Nenhuma variável sensível hardcoded no código

---

## 🟣 6️⃣ Persistência de Dados

- [ ] Volume configurado para arquivos estáticos
- [ ] Volume configurado para arquivos de mídia
- [ ] Reinício do container não apaga dados
- [ ] Banco mantém dados após restart

---

## 🔄 7️⃣ Validação Pós-Deploy

- [ ] Build finalizou sem erro
- [ ] Container inicia sem loop de reinício
- [ ] Logs mostram:
  - [ ] Espera do banco
  - [ ] collectstatic executado
  - [ ] migrate executado
  - [ ] Gunicorn iniciado
- [ ] Página principal carrega
- [ ] Admin acessível
- [ ] Arquivos estáticos carregam corretamente
- [ ] Upload de mídia funciona
- [ ] Push no GitHub gera novo deploy automático

---

## 🚨 8️⃣ Critérios que Invalidam o Deploy

Interromper imediatamente se:

- [ ] `runserver` aparece nos logs de produção
- [ ] `makemigrations` executa em produção
- [ ] `DEBUG=1` em produção
- [ ] Porta incorreta no proxy
- [ ] Falha de conexão com banco
- [ ] Container reinicia continuamente
- [ ] `uv.lock` não está versionado

---

# 🏁 DEPLOY APROVADO

O deploy é considerado validado apenas se **todos os itens acima estiverem marcados**.