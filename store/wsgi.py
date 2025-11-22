import os

from django.core.wsgi import get_wsgi_application

# Point to your settings file
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'store.settings')

application = get_wsgi_application()