from functools import wraps
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from .models import Project, Profile
from .forms import ProjectForm, ProfileForm
from .publishing import publish

def editor(view):
    @login_required
    @wraps(view)
    def inner(request, *args, **kwargs):
        if not request.user.is_active or not request.user.is_staff:
            raise PermissionDenied
        return view(request, *args, **kwargs)
    return inner

@editor
def dashboard(request):
    projects = Project.objects.all()
    return render(request, 'studio/dashboard.html', {'projects': projects, 'published_count': projects.filter(published=True).count(), 'draft_count': projects.filter(published=False).count()})

@editor
def project_edit(request, pk=None):
    project = get_object_or_404(Project, pk=pk) if pk else None
    form = ProjectForm(request.POST or None, instance=project)
    if request.method == 'POST' and form.is_valid():
        form.save()
        publish()
        messages.success(request, 'Project saved. Your public portfolio is up to date.')
        return redirect('dashboard')
    return render(request, 'studio/form.html', {'form': form, 'title': 'Edit project' if project else 'New project', 'subtitle': 'Project details.', 'project': project})

@editor
@require_POST
def project_delete(request, pk):
    get_object_or_404(Project, pk=pk).delete()
    publish()
    messages.success(request, 'Project deleted and portfolio updated.')
    return redirect('dashboard')

@editor
def profile_edit(request):
    profile, _ = Profile.objects.get_or_create(pk=1)
    form = ProfileForm(request.POST or None, instance=profile)
    if request.method == 'POST' and form.is_valid():
        form.save()
        publish()
        messages.success(request, 'Profile saved and portfolio updated.')
        return redirect('dashboard')
    return render(request, 'studio/form.html', {'form': form, 'title': 'Your profile', 'subtitle': 'Name, description, and contact links.'})
