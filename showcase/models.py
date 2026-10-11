from django.db import models
from django.core.validators import URLValidator, MinValueValidator, MaxValueValidator

https_only = URLValidator(schemes=['https'])

class Project(models.Model):
    CATEGORY_CHOICES = [('development', 'Development'), ('design', 'Design'), ('experiment', 'Experiment')]
    ART_CHOICES = [('orbit', 'Orbital / lime'), ('wave', 'Waveform / violet'), ('grid', 'Architecture / ice')]
    title = models.CharField(max_length=100)
    summary = models.CharField(max_length=220)
    description = models.TextField(max_length=6000, blank=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='development')
    tags = models.CharField(max_length=140, help_text='Comma-separated, e.g. Python, Django, Design')
    year = models.PositiveIntegerField(default=2026, validators=[MinValueValidator(2000), MaxValueValidator(2100)])
    artwork = models.CharField(max_length=12, choices=ART_CHOICES, default='orbit')
    cover_url = models.URLField(max_length=500, blank=True, validators=[https_only], help_text='Optional HTTPS image URL. Leave empty for animated artwork.')
    live_url = models.URLField(max_length=500, blank=True, validators=[https_only])
    source_url = models.URLField(max_length=500, blank=True, validators=[https_only])
    is_concept = models.BooleanField(default=False, help_text='Label illustrative work as a concept.')
    published = models.BooleanField(default=False)
    position = models.PositiveIntegerField(default=0, validators=[MaxValueValidator(9999)])
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['position', '-year', '-pk']

    @property
    def tag_list(self):
        return [tag.strip() for tag in self.tags.split(',') if tag.strip()][:8]

class Profile(models.Model):
    name = models.CharField(max_length=60, default='Robin')
    role = models.CharField(max_length=100, default='Developer & curious maker')
    headline = models.CharField(max_length=90, default='Building what comes next.')
    intro = models.TextField(max_length=400, default='A space for ideas, interfaces, and experiments. Exploring the place where thoughtful design meets working code.')
    about = models.TextField(max_length=2000, default='I like turning a what-if into something you can actually use. This is my collection of projects, small experiments, and things learned along the way.')
    location = models.CharField(max_length=80, blank=True, default='Estonia')
    availability = models.CharField(max_length=80, default='Open to interesting ideas')
    contact_email = models.EmailField(blank=True)
    github_url = models.URLField(blank=True, validators=[https_only])
    linkedin_url = models.URLField(blank=True, validators=[https_only])
