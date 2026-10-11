from django.core.management.base import BaseCommand
from showcase.models import Profile, Project
from showcase.publishing import publish
class Command(BaseCommand):
    help = 'Create profile and clearly labeled concept projects only on first setup.'
    def handle(self, *args, **options):
        _, first_setup = Profile.objects.get_or_create(pk=1)
        if first_setup and not Project.objects.exists():
            for i, (title, summary, category, tags, artwork) in enumerate([
                ('Orbit interface', 'A study in focus. An imagined workspace that brings a little calm to a complex world.', 'design', 'Interface design, Interaction', 'orbit'),
                ('Signal / noise', 'Exploring the rhythm between data, motion, and a more expressive web.', 'experiment', 'Creative coding, Motion', 'wave'),
                ('Small systems', 'An exploration of modular tools and the beauty of making complex things feel simple.', 'development', 'Systems, Prototyping', 'grid'),
            ]):
                Project.objects.create(title=title, summary=summary, description='An illustrative concept included to demonstrate this portfolio. Replace it with your own work in the private studio.', category=category, tags=tags, artwork=artwork, position=i, is_concept=True, published=True)
        publish()
        self.stdout.write('Portfolio initialized. Concept projects can be replaced in the studio.')
