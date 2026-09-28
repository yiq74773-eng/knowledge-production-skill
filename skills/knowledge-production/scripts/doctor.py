"""Read-only capability report; standard library only, no installations or UI actions."""
import argparse
import importlib.util
import json
import platform
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def report(mode="text", drafts_root=None):
    required = ["SKILL.md", "references/research.md", "references/production.md",
                "references/integrations.md", "vendor/text-cleanup/RULES.md"]
    missing = [name for name in required if not (ROOT / name).is_file()]
    result = {
        "platform": platform.system(), "python": platform.python_version(),
        "package_complete": not missing, "missing_files": missing,
        "mode": mode, "agent_capabilities": "Agent must check browsing, file access and UI tools separately.",
        "application_open_verified": False,
    }
    if mode == "jianying":
        runtime = ROOT / "vendor/jianying-editor/scripts/jy_wrapper.py"
        result.update({
            "bundled_runtime": runtime.is_file(),
            "pymediainfo_installed": importlib.util.find_spec("pymediainfo") is not None,
            "ffmpeg_available": shutil.which("ffmpeg") is not None,
            "ffprobe_available": shutil.which("ffprobe") is not None,
            "drafts_root_supplied": drafts_root is not None,
            "drafts_root_exists": bool(drafts_root and Path(drafts_root).expanduser().is_dir()),
            "native_jianying_candidate": platform.system() in ("Windows", "Darwin"),
            "note": "Module presence does not prove MediaInfo native-library or JianYing version compatibility.",
        })
        result["ready_for_draft_attempt"] = (
            not missing and result["bundled_runtime"] and result["pymediainfo_installed"]
            and result["drafts_root_supplied"]
        )
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("text", "jianying"), default="text")
    parser.add_argument("--drafts-root")
    args = parser.parse_args()
    result = report(args.mode, args.drafts_root)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["package_complete"] and (args.mode == "text" or result["ready_for_draft_attempt"]) else 2


if __name__ == "__main__":
    sys.exit(main())
