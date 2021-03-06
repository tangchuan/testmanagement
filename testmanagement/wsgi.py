"""
WSGI config for testmanagement project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

profile = os.environ.get('TESTMANAGEMENT_PROFILE', 'product')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "testmanagement.settings.%s" % profile)

application = get_wsgi_application()
