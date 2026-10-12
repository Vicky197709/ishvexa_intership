import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'error_ingestion.settings')
application = get_asgi_application()
