import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

REPO = Path(__file__).resolve().parents[1]
SKILL = REPO / "skills/knowledge-production"


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


builder = module("draft_builder", SKILL / "scripts/build_jianying.py")
installer = module("installer", REPO / "scripts/install_skill.py")


class PortableTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="knowledge-test-")
        self.root = Path(self.temp.name)
        (self.root / "assets").mkdir()
        (self.root / "assets/clip.mp4").write_bytes(b"test path only")

    def tearDown(self):
        self.temp.cleanup()

    def plan(self):
        return {"schema_version": 1, "name": "demo-v1", "width": 1080, "height": 1920, "fps": 30,
                "clips": [{"kind": "video", "media": "assets/clip.mp4", "start": 0, "source_start": 1, "duration": 2}],
                "captions": [{"text": "可能如此", "start": 0, "duration": 1}]}

    def test_relative_assets_survive_project_move(self):
        import shutil
        moved = self.root / "different device 中文" / "project"
        shutil.copytree(self.root / "assets", moved / "assets")
        builder.validate_plan(self.plan(), moved)

    def test_absolute_and_escaping_assets_rejected(self):
        for path in ("../outside.mp4", "C:/Users/someone/clip.mp4", "/tmp/clip.mp4", "assets\\clip.mp4"):
            with self.subTest(path=path), self.assertRaises(ValueError):
                builder.resolve_asset(path, self.root)

    def test_existing_draft_preserved(self):
        existing = self.root / "demo-v1"
        existing.mkdir()
        original = existing / "keep.txt"
        original.write_text("original", encoding="utf-8")
        with self.assertRaises(FileExistsError):
            builder.ensure_new_destination(self.root, "demo-v1")
        self.assertEqual(original.read_text(encoding="utf-8"), "original")

    def test_no_cross_purpose_audio_track(self):
        plan = self.plan()
        plan["clips"] += [dict(kind=kind, media="assets/clip.mp4", start=0, duration=1, track="Mixed")
                          for kind in ("narration", "bgm")]
        with self.assertRaises(ValueError):
            builder.validate_plan(plan, self.root)

    def test_invalid_timing_and_overlap_rejected(self):
        for value in (-1, float("nan"), True):
            plan = self.plan()
            plan["clips"][0]["duration"] = value
            with self.subTest(value=value), self.assertRaises(ValueError):
                builder.validate_plan(plan, self.root)
        plan = self.plan()
        plan["clips"].append(dict(plan["clips"][0], start=1))
        with self.assertRaises(ValueError):
            builder.validate_plan(plan, self.root)

    def test_install_relocates_and_never_overwrites(self):
        destination = self.root / "agent skills 中文"
        installed = installer.install(destination)
        self.assertTrue((installed / "vendor/text-cleanup/RULES.md").is_file())
        with self.assertRaises(FileExistsError):
            installer.install(destination)
        before = sorted(str(path.relative_to(installed)) for path in installed.rglob("*"))
        result = subprocess.run([sys.executable, "-B", str(installed / "scripts/doctor.py"), "--mode", "text"],
                                cwd=self.root, capture_output=True, text=True, encoding="utf-8", check=True)
        data = json.loads(result.stdout)
        self.assertTrue(data["package_complete"])
        self.assertFalse(data["application_open_verified"])
        after = sorted(str(path.relative_to(installed)) for path in installed.rglob("*"))
        self.assertEqual(before, after, "Doctor must not modify the installed package")


if __name__ == "__main__":
    unittest.main()
