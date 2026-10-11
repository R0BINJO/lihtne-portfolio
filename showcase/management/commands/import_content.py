"""Import reviewed public content without replacing accounts or unrelated projects."""
import json
from pathlib import Path
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from showcase.models import Profile, Project
from showcase.publishing import publish
from .export_content import PROFILE_FIELDS, PROJECT_FIELDS

class Command(BaseCommand):
    help = 'Import profile and projects from reviewed public JSON; remove starter concepts.'

    def add_arguments(self, parser):
        parser.add_argument('--content', type=Path, default=settings.BASE_DIR / 'content/portfolio.json')

    def handle(self, *args, **options):
        payload = json.loads(options['content'].read_text())
        if payload.get('schema_version') != 1:
            raise CommandError('Unsupported public content schema.')
        with transaction.atomic():
            profile, _ = Profile.objects.get_or_create(pk=1)
            for field in PROFILE_FIELDS:
                value = payload['profile'].get(field, getattr(profile, field))
                # Preserve already-configured contact links when the source has none.
                if field in ['contact_email', 'github_url', 'linkedin_url'] and not value:
                    continue
                setattr(profile, field, value)
            profile.full_clean()
            profile.save()
            for item in payload['projects']:
                matches = Project.objects.filter(title=item['title'])
                if matches.count() > 1:
                    raise CommandError('Duplicate project titles require manual reconciliation.')
                project = matches.first() or Project()
                for field in PROJECT_FIELDS:
                    if field != 'id' and field in item:
                        setattr(project, field, item[field])
                project.published = True
                project.full_clean()
                project.save()
            Project.objects.filter(is_concept=True, title__in=['Orbit interface', 'Signal / noise', 'Small systems']).delete()
        publish()
        self.stdout.write(f"Imported {len(payload['projects'])} published projects. Existing accounts and unrelated projects preserved.")
