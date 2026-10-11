"""Export the public profile and published projects, never accounts or drafts."""
import json
from django.core.management.base import BaseCommand
from showcase.models import Profile, Project

PROFILE_FIELDS = ['name', 'role', 'headline', 'intro', 'about', 'location', 'availability', 'contact_email', 'github_url', 'linkedin_url']
PROJECT_FIELDS = ['id', 'title', 'summary', 'description', 'category', 'tags', 'year', 'artwork', 'cover_url', 'live_url', 'source_url', 'is_concept', 'position']

class Command(BaseCommand):
    help = 'Write only publicly visible portfolio content as JSON to stdout.'

    def handle(self, *args, **options):
        profile = Profile.objects.get(pk=1)
        payload = {
            'schema_version': 1,
            'profile': {field: getattr(profile, field) for field in PROFILE_FIELDS},
            'projects': list(Project.objects.filter(published=True).values(*PROJECT_FIELDS)),
        }
        self.stdout.write(json.dumps(payload, ensure_ascii=False, indent=2))
