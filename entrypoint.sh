#!/bin/bash
set -e

echo "=== IncidentOps Campus – Démarrage ==="

# Wait for database
echo "Attente de la base de données..."
while ! python -c "
import psycopg2, os
try:
    conn = psycopg2.connect(
        dbname=os.environ.get('DB_NAME', 'incidentops_db'),
        user=os.environ.get('DB_USER', 'incidentops_user'),
        password=os.environ.get('DB_PASSWORD', 'password'),
        host=os.environ.get('DB_HOST', 'db'),
        port=os.environ.get('DB_PORT', '5432'),
    )
    conn.close()
except Exception:
    exit(1)
" 2>/dev/null; do
    echo "  Base de données non disponible, nouvelle tentative dans 2s..."
    sleep 2
done
echo "  Base de données prête !"

# Run migrations
echo "Exécution des migrations..."
python manage.py migrate --noinput

# Populate initial data
echo "Initialisation des données..."
python manage.py populate_data

# Collect static files
echo "Collecte des fichiers statiques..."
python manage.py collectstatic --noinput

# Start Gunicorn
echo "Démarrage de Gunicorn..."
exec gunicorn incidentops.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 3 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -
