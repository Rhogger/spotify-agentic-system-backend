#!/bin/sh

# Encerra o script se qualquer comando falhar
set -e

echo "🚀 Iniciando Container do Backend..."

# 1. Aplica Migrations (Garante que o banco tá atualizado)
echo "📦 Aplicando migrations do banco de dados..."
alembic upgrade head

# 2. Roda Seeds se precisar (import_tracks.py agora é seguro/idempotente)
echo "🌱 Verificando necessidade de seed..."
python scripts/import_tracks.py

# 3. Inicia o Servidor (Substitui o processo do shell pelo uvicorn)
echo "🔥 Iniciando servidor Uvicorn..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 $UVICORN_ARGS