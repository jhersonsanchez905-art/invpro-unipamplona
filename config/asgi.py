import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

from django.core.asgi import get_asgi_application
from starlette.routing import Mount
from starlette.applications import Starlette

django_asgi_app = get_asgi_application()

from api.main import app as fastapi_app

application = Starlette(routes=[
    Mount('/api', app=fastapi_app),
    Mount('/', app=django_asgi_app),
])