import json, subprocess, tempfile, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "project_registry.py"

class ProjectRegistryTest(unittest.TestCase):
    def test_render_refuses_overwrite_without_force(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "input.json"; out = Path(tmp) / "out"; out.mkdir()
            source.write_text(json.dumps({"name":"demo","path":"demo","card":"kb/projects/demo.md","server":"demo","module":".","main_class":"Demo","source_path":"src/Demo.java","description":"demo"}), encoding="utf-8")
            cmd = ["python3", str(SCRIPT), "render", "--input", str(source), "--output-dir", str(out)]
            self.assertEqual(subprocess.run(cmd, capture_output=True).returncode, 0)
            self.assertNotEqual(subprocess.run(cmd, capture_output=True).returncode, 0)
