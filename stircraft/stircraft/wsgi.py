"""
WSGI config for stircraft project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

# Use the correct settings module path for Heroku deployment
if 'DYNO' in os.environ:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stircraft.stircraft.settings')
else:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stircraft.settings')

application = get_wsgi_application()
