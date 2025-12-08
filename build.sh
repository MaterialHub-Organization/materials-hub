#!/usr/bin/env bash
# Salir si hay error
set -o errexit

echo "✅ build.sh iniciado"

# Instalar dependencias
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install -e .

# Setup de la base de datos y seeders (con -y para evitar confirmación interactiva)
rosemary db:setup -y

echo "✅ build.sh finalizado"