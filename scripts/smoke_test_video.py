"""Generate synthetic media and verify an isolated draft. Requires pymediainfo and FFmpeg."""
import argparse
import importlib.util
import json
import math
from pathlib import Path
import shutil
import struct
import subprocess
import sys
import tempfile
import wave

REPO = Path(__file__).resolve().parents[1]


def run(root):
    spec = importlib.util.spec_from_file_location("portable_builder", REPO / "skills/knowledge-production/scripts/build_jianying.py")
    builder = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(builder)
    executable = shutil.which("ffmpeg")
    if not executable:
        import imageio_ffmpeg
        executable = imageio_ffmpeg.get_ffmpeg_exe()
    source = root / "source project 中文"
    (source / "assets").mkdir(parents=True)
    subprocess.run([executable, "-hide_banner", "-loglevel", "error", "-f", "lavfi", "-i",
                    "color=c=0x244F58:s=640x360:r=30", "-t", "4", "-c:v", "libx264", "-pix_fmt", "yuv420p",
                    str(source / "assets/test.mp4")], check=True)
    with wave.open(str(source / "assets/test.wav"), "wb") as audio:
        audio.setnchannels(1)
        audio.setsampwidth(2)
        audio.setframerate(48000)
        audio.writeframes(b"".join(struct.pack("<h", round(800 * math.sin(2 * math.pi * 220 * i / 48000))) for i in range(4 * 48000)))
    plan = {
        "schema_version": 1, "name": "portable-smoke-v1", "width": 1080, "height": 1920, "fps": 30,
        "clips": [
            {"kind": "video", "media": "assets/test.mp4", "start": 0, "source_start": 0.5, "duration": 2},
            {"kind": "narration", "media": "assets/test.wav", "start": 0, "source_start": 0.2, "duration": 1},
            {"kind": "original", "media": "assets/test.wav", "start": 1, "source_start": 1, "duration": 1},
            {"kind": "bgm", "media": "assets/test.wav", "start": 0, "source_start": 0.5, "duration": 2, "volume": 0.05}],
        "captions": [{"text": "工程数据检查", "start": 0, "duration": 1}, {"text": "不代表实际听看验收", "start": 1, "duration": 1}],
    }
    manifest = source / "edit-plan.json"
    manifest.write_text(json.dumps(plan, ensure_ascii=False), encoding="utf-8")
    result = builder.build(manifest, root / "drafts")
    draft = Path(result["draft_path"])
    candidates = [draft / "draft_info.json", draft / "draft_content.json"]
    content = json.loads(next(path for path in candidates if path.exists()).read_text(encoding="utf-8"))
    tracks = content["tracks"]
    types = [track["type"] for track in tracks]
    assert types.count("video") == 1 and types.count("audio") == 3 and types.count("text") == 1, types
    video = next(track for track in tracks if track["type"] == "video")["segments"][0]
    assert video["source_timerange"]["start"] == 500000
    assert video["target_timerange"]["duration"] == 2000000
    source_starts = sorted(track["segments"][0]["source_timerange"]["start"] for track in tracks if track["type"] == "audio")
    assert source_starts == [200000, 500000, 1000000], source_starts
    assert content["canvas_config"]["width"] == 1080 and content["canvas_config"]["height"] == 1920
    assert not (draft / "BUILD_INCOMPLETE.txt").exists()
    portable = json.loads((draft / "production-plan.json").read_text(encoding="utf-8"))
    moved = root / "another device" / "copied draft"
    shutil.copytree(draft, moved)
    builder.validate_plan(portable, moved)
    # Rebuild in another path to prove media are no longer tied to the source machine's directory.
    rebuilt = builder.build(moved / "production-plan.json", root / "new device drafts")
    assert rebuilt["clips"] == 4
    return {"status": "passed", "tracks": types, "video_source_offset_us": 500000,
            "audio_source_offsets_us": source_starts, "relative_plan_rebuild": True,
            "application_open_verified": False, "exported": False}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="New/empty isolated test directory; otherwise temporary")
    args = parser.parse_args()
    if args.output:
        if args.output.exists() and any(args.output.iterdir()):
            parser.error("Output directory must be empty")
        result = run(args.output.resolve())
    else:
        with tempfile.TemporaryDirectory(prefix="knowledge-video-smoke-") as temporary:
            result = run(Path(temporary))
    print(json.dumps(result, ensure_ascii=False, indent=2))
