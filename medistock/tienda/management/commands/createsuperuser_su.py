from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    help = 'Crea un superusuario sys92X si no existe.'

    def handle(self, *args, **options):
        User = get_user_model()
        username = 'sys92X'
        email = 'admin@example.com'
        password = 'A@entrar29Xw'

        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.WARNING(f'El superusuario {username} ya existe.'))
            return

        User.objects.create_superuser(username=username, email=email, password=password)
        self.stdout.write(self.style.SUCCESS(f'Superusuario {username} creado correctamente.'))
