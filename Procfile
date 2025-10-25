web: python manage.py migrate && python manage.py collectstatic --noinput && daphne -b 0.0.0.0 -p $PORT bridgedash.asgi:application
worker: celery -A bridgedash worker --loglevel=info