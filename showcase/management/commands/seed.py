from django.core.management import call_command
from django.core.management.base import BaseCommand
from showcase.models import Profile
from showcase.publishing import publish

class Command(BaseCommand):
    help = 'Initialize a new portfolio from the reviewed public-content snapshot.'

    def handle(self, *args, **options):
        if not Profile.objects.filter(pk=1).exists():
            call_command('import_content')
        else:
            publish()
            self.stdout.write('Existing portfolio preserved and exported.')
