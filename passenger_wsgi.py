import os
import sys

# Change to the application directory (the project root)
os.chdir(os.path.dirname(__file__))

# Add the current directory to the Python path
sys.path.insert(0, '.') 

# Set the correct settings module name: 'store.settings'
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'store.settings') 

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()