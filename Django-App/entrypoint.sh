#!/bin/sh

python manage.py migrate --noinput
python manage.py makemigrations order_service --noinput
python manage.py migrate --noinput

echo "Setting up superuser"
echo "from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'devin.mens@gmail.com', 'nimda')" | python manage.py shell
mkdir -p logs
touch ./logs/gunicorn.log
touch ./logs/gunicorn-access.log
tail -n 0 -f ./logs/gunicorn*.log &

export DJANGO_SETTINGS_MODULE=kyma_order.settings

exec gunicorn kyma_order.wsgi:application \
    --name kyma_order \
    --bind 0.0.0.0:8000 \
    --workers 5 \
    --log-level=info \
    --log-file=./logs/gunicorn.log \
    --access-logfile=./logs/gunicorn-access.log \

"$@"