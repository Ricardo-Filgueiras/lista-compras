#!/bin/sh
set -e

# Se as env vars de Postgres existirem, aguarda o banco
if [ -n "$POSTGRES_HOST" ] && [ -n "$POSTGRES_PORT" ]; then
  until pg_isready -h "$POSTGRES_HOST" -p "$POSTGRES_PORT"; do
    echo "🟡 Waiting for Postgres Database Startup ($POSTGRES_HOST:$POSTGRES_PORT) ..."
    sleep 2
  done
  echo "✅ Postgres Database Started Successfully ($POSTGRES_HOST:$POSTGRES_PORT)"
fi

# Produção: NÃO roda makemigrations
python manage.py collectstatic --noinput
python manage.py migrate --noinput

# Sobe aplicação com Gunicorn
start_gunicorn.sh