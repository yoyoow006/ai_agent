import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / 'project_registry.py'


class ProjectRegistryTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.input = self.root / 'input.json'
        self.out = self.root / 'draft'
        self.data = dict(name='library', path='modules/library', build='python', card='kb/projects/library.md', description='Shared helpers', applications=[])

    def run_cli(self, *args):
        return subprocess.run([sys.executable, str(SCRIPT), *args], text=True, capture_output=True)

    def render(self, *args):
        self.input.write_text(json.dumps(self.data))
        return self.run_cli('render', '--input', str(self.input), '--output-dir', str(self.out), *args)

    def test_library_and_legacy_application_drafts_validate(self):
        for legacy in (False, True):
            with self.subTest(legacy=legacy):
                if legacy:
                    self.data.pop('applications')
                    self.data.update(server='api', module='.', main_class='main', source_path='src/main.py')
                result = self.render('--force')
                self.assertEqual(0, result.returncode, result.stderr)
                entry = json.loads((self.out / 'registry-entry.json').read_text())
                self.assertEqual(int(legacy), len(entry['applications']))
                cards = self.root / '.ai/kb/projects'
                cards.mkdir(parents=True, exist_ok=True)
                (cards / 'library.md').write_text((self.out / 'library.md').read_text())
                (cards / 'registry.json').write_text(json.dumps({'schema_version':1, 'projects':[entry]}))
                validated = self.run_cli('validate', '--workspace', str(self.root))
                self.assertEqual(0, validated.returncode, validated.stderr)

    def test_invalid_inputs_create_no_outputs(self):
        original = self.data.copy()
        for update in [dict(build=None), dict(build=''), dict(path='../escape'), dict(card='/tmp/card.md'), dict(card='../card.md'), dict(card='rules-index-entry.md'), dict(card='registry-entry.json'), dict(applications={}), dict(applications=[{}]), dict(applications=[dict(server='x',module='..',main_class='m',source_path='src')]), dict(description=[]), dict(business_terms='bad')]:
            self.data = {**original, **update}
            with self.subTest(update=update):
                self.assertNotEqual(0, self.render().returncode)
                self.assertFalse(self.out.exists())
        self.data = original.copy()
        del self.data['build']
        self.assertNotEqual(0, self.render().returncode)

    def test_every_existing_output_is_protected_before_any_write(self):
        for name in ('registry-entry.json', 'library.md', 'rules-index-entry.md'):
            self.out.mkdir(exist_ok=True)
            target = self.out / name
            target.write_text('keep')
            result = self.render()
            self.assertNotEqual(0, result.returncode)
            self.assertEqual('keep', target.read_text())
            self.assertEqual([name], [p.name for p in self.out.iterdir()])
            target.unlink()
        self.assertEqual(0, self.render().returncode)
        self.assertEqual(0, self.render('--force').returncode)

    def test_symlink_outputs_are_rejected_even_with_force(self):
        real = self.root / 'real'
        real.mkdir()
        self.out.symlink_to(real, target_is_directory=True)
        self.assertNotEqual(0, self.render('--force').returncode)
        self.assertEqual([], list(real.iterdir()))
        self.out.unlink()
        self.out.mkdir()
        target = real / 'keep'
        target.write_text('keep')
        (self.out / 'registry-entry.json').symlink_to(target)
        self.assertNotEqual(0, self.render('--force').returncode)
        self.assertEqual('keep', target.read_text())

    def test_validate_invalid_registry_fails(self):
        result = self.run_cli('validate', '--workspace', str(self.root))
        self.assertNotEqual(0, result.returncode)
        self.assertIn('ERROR', result.stderr)
