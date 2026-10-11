import io
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from django.core.management import call_command
from django.test import TestCase, SimpleTestCase
from showcase.models import Profile, Project

ROOT = Path(__file__).resolve().parent.parent

class PublicContentExportTests(TestCase):
    def test_only_published_content_leaves_private_database(self):
        Profile.objects.create(pk=1, name='Public name')
        Project.objects.create(title='Visible project', summary='Public body', tags='Python', published=True)
        Project.objects.create(title='HIDDEN DRAFT', summary='HIDDEN BODY', tags='', published=False)
        output=io.StringIO()
        call_command('export_content', stdout=output)
        payload=json.loads(output.getvalue())
        self.assertEqual(payload['profile']['name'],'Public name')
        self.assertEqual(len(payload['projects']),1)
        self.assertEqual(payload['projects'][0]['title'],'Visible project')
        self.assertNotIn('HIDDEN DRAFT',output.getvalue())
        self.assertNotIn('HIDDEN BODY',output.getvalue())
        self.assertNotIn('password',output.getvalue())
        self.assertNotIn('updated_at',payload['projects'][0])

class PagesBuildTests(SimpleTestCase):
    def test_pages_build_paths_escaping_and_public_artifact(self):
        payload=json.loads((ROOT/'content/portfolio.json').read_text())
        payload['profile']['name']='Private real name'
        payload['profile']['intro']='<script>UNSAFE_TEST</script>'
        with tempfile.TemporaryDirectory() as directory:
            directory=Path(directory)
            source=directory/'content.json'
            source.write_text(json.dumps(payload))
            for index,base in enumerate(['/lihtne-portfolio','']):
                output=directory/f'build-{index}'
                result=subprocess.run([sys.executable,str(ROOT/'scripts/build_pages.py'),'--content',str(source),'--output',str(output),'--base-path',base],capture_output=True,text=True)
                self.assertEqual(result.returncode,0,result.stderr)
                html=(output/'index.html').read_text()
                self.assertIn(f'href="{base}/static/site.css?v=green-landing-r"',html)
                self.assertIn(f'src="{base}/static/site.js"',html)
                self.assertNotIn('Private real name',html)
                self.assertIn('<title>My portfolio</title>',html)
                self.assertNotIn('class="brand-mark"',html)
                self.assertIn('id="contact-title">Contact me',html)
                self.assertNotIn('<script>UNSAFE_TEST',html)
                self.assertIn('&lt;script&gt;UNSAFE_TEST',html)
                self.assertIn('http-equiv="Content-Security-Policy"',html)
                files={str(path.relative_to(output)) for path in output.rglob('*') if path.is_file()}
                expected_images={f'static/{project["cover_asset"]}' for project in payload['projects'] if project.get('cover_asset')}
                self.assertEqual(files,expected_images | {'index.html','404.html','robots.txt','.nojekyll','static/site.css','static/site.js','static/favicon.svg','static/fonts/space-grotesk.ttf','static/fonts/OFL.txt'})
                self.assertIn("url('fonts/space-grotesk.ttf')",(output/'static/site.css').read_text())

class PublicContentImportTests(TestCase):
    def test_import_replaces_starters_preserves_unrelated_work_and_contact(self):
        Profile.objects.create(pk=1, name='Before import', contact_email='owner@example.com')
        starter=Project.objects.create(title='Orbit interface',summary='Demo',tags='Demo',is_concept=True,published=True)
        custom=Project.objects.create(title='Unrelated project',summary='Keep',tags='Keep',published=True)
        call_command('import_content',stdout=io.StringIO())
        custom.refresh_from_db()
        self.assertFalse(Project.objects.filter(pk=starter.pk).exists())
        self.assertTrue(custom.published)
        self.assertEqual(Profile.objects.get(pk=1).contact_email,'owner@example.com')
        self.assertEqual(Project.objects.filter(published=True).count(),7)
        self.assertEqual(Project.objects.exclude(cover_asset='').count(),4)
        self.assertFalse(Project.objects.get(title='acq').cover_asset)
        self.assertFalse(Project.objects.get(title='My own environment').cover_asset)

    def test_invalid_bundled_image_rolls_back_import(self):
        from django.core.exceptions import ValidationError
        Profile.objects.create(pk=1,name='Original profile')
        payload=json.loads((ROOT/'content/portfolio.json').read_text())
        payload['projects'][0]['cover_asset']='../private/secret.key'
        with tempfile.TemporaryDirectory() as directory:
            source=Path(directory)/'content.json'
            source.write_text(json.dumps(payload))
            with self.assertRaises(ValidationError):
                call_command('import_content',content=source,stdout=io.StringIO())
        self.assertEqual(Profile.objects.get(pk=1).name,'Original profile')
        self.assertEqual(Project.objects.count(),0)
