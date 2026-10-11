from django import forms
from .models import Project, Profile

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['title', 'summary', 'description', 'category', 'tags', 'year', 'artwork', 'cover_url', 'live_url', 'source_url', 'position', 'is_concept', 'published']
        widgets = {'description': forms.Textarea(attrs={'rows': 6})}

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        exclude = ['id']
        widgets = {'intro': forms.Textarea(attrs={'rows': 3}), 'about': forms.Textarea(attrs={'rows': 6})}
