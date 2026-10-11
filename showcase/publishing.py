import os
import tempfile
from django.conf import settings
from django.template.loader import render_to_string
from .models import Profile, Project

def publish():
    """Only explicitly published content crosses into the public directory."""
    root = settings.PUBLISHED_DIR
    root.mkdir(mode=0o755, parents=True, exist_ok=True)
    profile, _ = Profile.objects.get_or_create(pk=1)
    html = render_to_string('index.html', {'profile': profile, 'projects': Project.objects.filter(published=True)})
    fd, temporary = tempfile.mkstemp(prefix='.publish-', dir=root)
    try:
        with os.fdopen(fd, 'w') as file:
            file.write(html)
            file.flush()
            os.fsync(file.fileno())
        os.chmod(temporary, 0o644)
        os.replace(temporary, root / 'index.html')
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
