import tempfile
from pathlib import Path
from io import BytesIO
from unittest.mock import patch
from django.test import TestCase, Client, override_settings
from django.contrib.auth import get_user_model
from showcase.models import Project, Profile
from showcase.forms import ProjectForm, ProfileForm
from showcase.publishing import publish
import serve_public

@override_settings(ALLOWED_HOSTS=['testserver', 'localhost'])
class StudioSecurityTests(TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.settings_override = override_settings(PUBLISHED_DIR=Path(self.directory.name))
        self.settings_override.enable()
        self.addCleanup(self.settings_override.disable)
        self.user = get_user_model().objects.create_user('editor', password='long-test-password-726!', is_staff=True)
        self.project = Project.objects.create(title='Public sample', summary='Description', tags='Python', published=True)

    def test_anonymous_admin_requires_login(self):
        for route in ['/admin/', '/admin/projects/new/', '/admin/profile/', f'/admin/projects/{self.project.pk}/']:
            self.assertEqual(self.client.get(route).status_code, 302)
        self.assertEqual(self.client.post(f'/admin/projects/{self.project.pk}/delete/').status_code, 302)
        self.assertTrue(Project.objects.filter(pk=self.project.pk).exists())

    def test_nonstaff_user_cannot_manage_projects(self):
        user = get_user_model().objects.create_user('visitor', password='long-test-password-726!')
        self.client.force_login(user)
        self.assertEqual(self.client.get('/admin/').status_code, 403)
        self.assertEqual(self.client.post(f'/admin/projects/{self.project.pk}/delete/').status_code, 403)

    def test_csrf_is_required_for_mutations_and_login(self):
        client = Client(enforce_csrf_checks=True)
        self.assertEqual(client.post('/admin/login/', {'username':'editor', 'password':'long-test-password-726!'}).status_code, 403)
        client.force_login(self.user)
        self.assertEqual(client.post(f'/admin/projects/{self.project.pk}/delete/').status_code, 403)

    def test_get_cannot_delete_or_logout(self):
        self.client.force_login(self.user)
        self.assertEqual(self.client.get(f'/admin/projects/{self.project.pk}/delete/').status_code, 405)
        self.assertEqual(self.client.get('/admin/logout/').status_code, 405)

    def test_drafts_never_enter_export(self):
        Project.objects.create(title='PRIVATE DRAFT SECRET', summary='PRIVATE BODY', tags='', published=False)
        publish()
        html = (Path(self.directory.name) / 'index.html').read_text()
        self.assertIn('Public sample', html)
        self.assertNotIn('PRIVATE DRAFT SECRET', html)
        self.assertNotIn('PRIVATE BODY', html)
        self.assertNotIn('csrfmiddlewaretoken', html)

    def test_project_and_profile_content_are_escaped(self):
        self.project.title = '<script>alert(1)</script>'
        self.project.description = '<img src=x onerror=alert(1)>'
        self.project.save()
        Profile.objects.create(pk=1, name='<script>alert(2)</script>')
        publish()
        html = (Path(self.directory.name) / 'index.html').read_text()
        self.assertNotIn('<script>alert(', html)
        self.assertNotIn('<img src=x', html)
        self.assertIn('&lt;script&gt;', html)

    def test_unsafe_urls_rejected(self):
        for url in ['javascript:alert(1)', 'data:text/html,test', 'http://insecure.example', 'file:///etc/passwd']:
            form = ProfileForm({'name':'Robin', 'role':'Builder', 'headline':'Hello', 'intro':'Intro', 'about':'About', 'availability':'Hello', 'github_url':url})
            self.assertFalse(form.is_valid())
            self.assertIn('github_url', form.errors)
        data = {'title':'X','summary':'Y','tags':'Z','category':'development','year':2026,'artwork':'orbit','position':0,'live_url':'javascript:alert(1)'}
        self.assertFalse(ProjectForm(data).is_valid())

    def test_authenticated_crud_updates_export(self):
        self.client.force_login(self.user)
        data = {'title':'A real project','summary':'Built today','description':'Details','category':'development','tags':'Python','year':2026,'artwork':'grid','position':0,'published':'on'}
        response = self.client.post('/admin/projects/new/', data)
        self.assertEqual(response.status_code,302)
        project = Project.objects.get(title='A real project')
        self.assertIn('A real project', (Path(self.directory.name)/'index.html').read_text())
        data['title'] = 'Edited project'
        self.assertEqual(self.client.post(f'/admin/projects/{project.pk}/',data).status_code,302)
        self.assertIn('Edited project', (Path(self.directory.name)/'index.html').read_text())
        data.pop('published')
        self.client.post(f'/admin/projects/{project.pk}/', data)
        self.assertNotIn('Edited project', (Path(self.directory.name)/'index.html').read_text())
        self.assertEqual(self.client.post(f'/admin/projects/{project.pk}/delete/').status_code,302)
        self.assertFalse(Project.objects.filter(pk=project.pk).exists())

    def test_login_throttle(self):
        for _ in range(5):
            response = self.client.post('/admin/login/', {'username':'editor','password':'wrong'})
        self.assertEqual(response.status_code,429)
        response = self.client.post('/admin/login/', {'username':'editor','password':'long-test-password-726!'})
        self.assertEqual(response.status_code,429)

    def test_external_login_redirect_is_rejected(self):
        response = self.client.post('/admin/login/', {'username':'editor','password':'long-test-password-726!', 'next':'https://evil.example/'})
        self.assertEqual(response.url, '/admin/')

    def test_session_and_headers(self):
        response = self.client.post('/admin/login/', {'username':'editor','password':'long-test-password-726!'})
        self.assertTrue(response.cookies['sessionid']['httponly'])
        self.assertEqual(response.cookies['sessionid']['samesite'], 'Strict')
        response = self.client.get('/admin/')
        self.assertEqual(response['Cache-Control'], 'no-store')
        self.assertEqual(response['Referrer-Policy'], 'same-origin')
        self.assertIn("frame-ancestors 'none'", response['Content-Security-Policy'])
        self.assertNotIn('unsafe-inline', response['Content-Security-Policy'])
        self.assertEqual(response['X-Content-Type-Options'], 'nosniff')

    def test_untrusted_host_is_rejected(self):
        self.assertEqual(self.client.get('/admin/login/', HTTP_HOST='evil.example').status_code,400)

class PublicSecurityTests(TestCase):
    def request(self, path, method='GET'):
        result = {}
        def start(status, headers, exc_info=None):
            result.update(status=status, headers=dict(headers))
        environ={'REQUEST_METHOD':method,'PATH_INFO':path,'SERVER_NAME':'localhost','SERVER_PORT':'8090','SERVER_PROTOCOL':'HTTP/1.1','wsgi.url_scheme':'http','wsgi.input':BytesIO(b''),'wsgi.errors':BytesIO()}
        result['body'] = b''.join(serve_public.application(environ,start))
        return result

    def test_public_surface_never_exposes_admin_or_private_files(self):
        for path in ['/admin/', '/admin/login/', '/private/db.sqlite3', '/private/secret.key', '/static/../private/secret.key', '/static/%2e%2e/private/secret.key', '/.env', '/manage.py', '/api/projects', '/static/../../serve_admin.py']:
            self.assertEqual(self.request(path)['status'], '404 Not Found', path)

    def test_all_public_mutations_rejected(self):
        for method in ['POST','PUT','PATCH','DELETE','TRACE','OPTIONS']:
            self.assertEqual(self.request('/',method)['status'],'405 Method Not Allowed')

    def test_static_assets_and_errors_have_security_headers(self):
        for path in ['/static/site.css','/static/site.js','/healthz','/missing']:
            result=self.request(path)
            self.assertEqual(result['headers']['X-Frame-Options'],'DENY')
            self.assertIn("form-action 'none'",result['headers']['Content-Security-Policy'])
            self.assertIn('Strict-Transport-Security',result['headers'])
            self.assertNotIn('Set-Cookie', result['headers'])

    def test_public_refreshes_export_and_supports_head(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(serve_public, 'PUBLIC', Path(directory)):
            self.assertEqual(self.request('/')['status'],'503 Service Unavailable')
            file=Path(directory)/'index.html'
            file.write_text('version one')
            self.assertEqual(self.request('/')['body'],b'version one')
            file.write_text('version two')
            self.assertEqual(self.request('/')['body'],b'version two')
            self.assertEqual(self.request('/','HEAD')['body'],b'')
