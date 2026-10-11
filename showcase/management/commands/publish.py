from django.core.management.base import BaseCommand
from showcase.publishing import publish
class Command(BaseCommand):
    help = 'Atomically export only published projects to the public site.'
    def handle(self, *args, **options):
        publish()
        self.stdout.write('Public portfolio exported.')
