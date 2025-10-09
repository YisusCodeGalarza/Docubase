from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
import os

class Command(BaseCommand):
    """
    Crea un superusuario si no existe ninguno.
    Lee las credenciales de las variables de entorno para mayor seguridad.
    """
    help = 'Crea un superusuario si no existe ninguno.'

    def handle(self, *args, **options):
        if User.objects.filter(is_superuser=True).exists():
            self.stdout.write(self.style.SUCCESS('Un superusuario ya existe. No se hace nada.'))
            return

        username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
        email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@example.com')
        password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')

        if not password:
            self.stderr.write(self.style.ERROR('La variable de entorno DJANGO_SUPERUSER_PASSWORD no está configurada.'))
            return

        User.objects.create_superuser(username=username, email=email, password=password)
        self.stdout.write(self.style.SUCCESS(f'Superusuario "{username}" creado exitosamente.'))
