web: python ap/manage.py collectstatic --noinput; gunicorn -b 0.0.0.0:$PORT --pythonpath=./ap ap.wsgi:application
