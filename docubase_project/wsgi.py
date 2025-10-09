import os
import django
from django.core.management import call_command
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'docubase_project.settings')

django.setup()
call_command('migrate')

application = get_wsgi_application()
