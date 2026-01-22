import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

# Point to the correct wsgi file
from store.wsgi import application
