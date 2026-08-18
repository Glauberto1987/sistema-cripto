#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate

# Codigo para burlar a falta de Shell e criar o SuperUser silenciosamente
python manage.py shell <<EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='glauberto').exists():
    User.objects.create_superuser('glauberto', 'admin@email.com', 'admin123')
EOF