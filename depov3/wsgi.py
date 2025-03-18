"""
WSGI config for depov3 project.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'depov3.settings')

application = get_wsgi_application()
app = application 