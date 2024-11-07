"""
ASGI config for src project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from messaging import routing

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_management.settings")

django_asgi_app = get_asgi_application()
application = ProtocolTypeRouter(
    {"http": django_asgi_app, "websocket": URLRouter(routing.websocket_urlpatterns)}
)
