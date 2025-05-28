#!/usr/bin/env bash
set -a
source .env        # carga tus variables de entorno
set +a

echo "Creando tablas..."
psql "$DATABASE_URL" -f sql/create_tables.sql

echo "Creando funciones..."
psql "$DATABASE_URL" -f sql/functions.sql

echo "✅ Tablas y funciones creadas."
