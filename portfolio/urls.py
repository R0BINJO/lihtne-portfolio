from django.urls import path
from django.contrib.auth import views as auth
from django.shortcuts import redirect
from showcase import views

urlpatterns = [
    path('', lambda request: redirect('dashboard')),
    path('admin/', views.dashboard, name='dashboard'),
    path('admin/login/', auth.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('admin/logout/', auth.LogoutView.as_view(), name='logout'),
    path('admin/password/', auth.PasswordChangeView.as_view(template_name='studio/form.html', success_url='/admin/', extra_context={'title': 'Change password', 'subtitle': 'Use a unique password of at least 14 characters.'}), name='password'),
    path('admin/projects/new/', views.project_edit, name='project_new'),
    path('admin/projects/<int:pk>/', views.project_edit, name='project_edit'),
    path('admin/projects/<int:pk>/delete/', views.project_delete, name='project_delete'),
    path('admin/profile/', views.profile_edit, name='profile_edit'),
]
