#!/bin/sh
set -e

# Permite ajuste por env vars sem mudar o código
: "${PORT:=8000}"
: "${GUNICORN_WORKERS:=2}"
: "${GUNICORN_THREADS:=4}"
: "${GUNICORN_TIMEOUT:=60}"

# Forçamos a porta 8000 pois portas < 1024 (como a 80) exigem root
# O EasyPanel deve ser configurado com "Proxy Port: 8000"
exec gunicorn core.wsgi:application \
  --bind "0.0.0.0:8000" \
  --workers "${GUNICORN_WORKERS}" \
  --threads "${GUNICORN_THREADS}" \
  --timeout "${GUNICORN_TIMEOUT}"