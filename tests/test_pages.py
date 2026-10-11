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
        payload['profile']['name']='<script>UNSAFE_TEST</script>'
        with tempfile.TemporaryDirectory() as directory:
            directory=Path(directory)
            source=directory/'content.json'
            source.write_text(json.dumps(payload))
            for index,base in enumerate(['/lihtne-portfolio','']):
                output=directory/f'build-{index}'
                result=subprocess.run([sys.executable,str(ROOT/'scripts/build_pages.py'),'--content',str(source),'--output',str(output),'--base-path',base],capture_output=True,text=True)
                self.assertEqual(result.returncode,0,result.stderr)
                html=(output/'index.html').read_text()
                self.assertIn(f'href="{base}/static/site.css"',html)
                self.assertIn(f'src="{base}/static/site.js"',html)
                self.assertNotIn('<script>UNSAFE_TEST',html)
                self.assertIn('&lt;script&gt;UNSAFE_TEST',html)
                self.assertIn('http-equiv="Content-Security-Policy"',html)
                files={str(path.relative_to(output)) for path in output.rglob('*') if path.is_file()}
                self.assertEqual(files,{'index.html','404.html','robots.txt','.nojekyll','static/site.css','static/site.js','static/favicon.svg','static/fonts/space-grotesk.ttf','static/fonts/OFL.txt'})
                self.assertIn("url('fonts/space-grotesk.ttf')",(output/'static/site.css').read_text())
