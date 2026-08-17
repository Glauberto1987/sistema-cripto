#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate
python manage.py shell -c "from django.contrib.auth.models import User; User.objects.filter(username='glauberto').exists() or User.objects.create_superuser('glauberto', 'a@a.com', 'admin123')"