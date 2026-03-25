#!/bin/sh
set -e

# Permite ajuste por env vars sem mudar o código
: "${PORT:=8000}"
: "${GUNICORN_WORKERS:=2}"
: "${GUNICORN_THREADS:=4}"
: "${GUNICORN_TIMEOUT:=60}"

# Ajuste o módulo se o seu wsgi estiver em outro caminho
# Ex.: "setup.wsgi:application" é o padrão comum quando o projeto Django se chama "setup".
exec gunicorn setup.wsgi:application \
  --bind "0.0.0.0:${PORT}" \
  --workers "${GUNICORN_WORKERS}" \
  --threads "${GUNICORN_THREADS}" \
  --timeout "${GUNICORN_TIMEOUT}"