"""Build a NEW editable draft from relative assets. Does not export or operate the UI."""
import argparse
import contextlib
import json
import math
import os
from pathlib import Path, PureWindowsPath
import re
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
KINDS = {"video": "Video", "narration": "Narration", "original": "OriginalAudio", "bgm": "BGM"}


def number(value, label, minimum=0, positive=False):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError(f"{label} must be a finite number")
    if value < minimum or (positive and value <= 0):
        raise ValueError(f"{label} is outside its valid range")
    return float(value)


def resolve_asset(value, project_root):
    if not isinstance(value, str) or not value:
        raise ValueError("media must be a non-empty relative path")
    # Reject Windows absolute paths even when running on macOS/Linux.
    if Path(value).is_absolute() or PureWindowsPath(value).drive or "\\" in value:
        raise ValueError("Use portable relative asset paths with '/' separators")
    root = Path(project_root).resolve()
    asset = (root / value).resolve()
    if not asset.is_relative_to(root):
        raise ValueError("Asset escapes the project directory")
    if not asset.is_file():
        raise ValueError(f"Missing asset: {value}")
    return asset


def validate_plan(plan, project_root):
    if not isinstance(plan, dict) or plan.get("schema_version") != 1:
        raise ValueError("Expected schema_version: 1")
    name = plan.get("name", "")
    if not isinstance(name, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,79}", name):
        raise ValueError("name must be a portable 1-80 character identifier: letters, digits, '_' or '-'")
    if re.fullmatch(r"(?i:CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])", name):
        raise ValueError("Reserved device name")
    for field in ("width", "height", "fps"):
        value = plan.get(field)
        if type(value) is not int or value <= 0:
            raise ValueError(f"{field} must be a positive integer")
    clips = plan.get("clips")
    if not isinstance(clips, list) or not clips or not any(c.get("kind") == "video" for c in clips if isinstance(c, dict)):
        raise ValueError("At least one video clip is required")
    track_kinds, intervals = {}, {}
    for clip in clips:
        if not isinstance(clip, dict) or clip.get("kind") not in KINDS:
            raise ValueError("Unknown clip kind")
        resolve_asset(clip.get("media"), project_root)
        start = number(clip.get("start"), "start")
        duration = number(clip.get("duration"), "duration", positive=True)
        number(clip.get("source_start", 0), "source_start")
        volume = number(clip.get("volume", 0 if clip["kind"] == "video" else 1), "volume")
        if volume > 4:
            raise ValueError("volume exceeds 4; check the mixing plan")
        track = clip.get("track", KINDS[clip["kind"]])
        if not isinstance(track, str) or not track.strip():
            raise ValueError("track must be non-empty text")
        kind = clip["kind"]
        if track in track_kinds and track_kinds[track] != kind:
            raise ValueError("Video, narration, original audio and BGM must use separate tracks")
        track_kinds[track] = kind
        intervals.setdefault(track, []).append((start, start + duration))
    for track, ranges in intervals.items():
        ordered = sorted(ranges)
        if any(current[0] < previous[1] - 0.000001 for previous, current in zip(ordered, ordered[1:])):
            raise ValueError(f"Overlapping clips on track {track}; put deliberate overlays on separate tracks")
    captions = plan.get("captions", [])
    if not isinstance(captions, list):
        raise ValueError("captions must be a list")
    for caption in captions:
        if not isinstance(caption, dict) or not isinstance(caption.get("text"), str) or not caption["text"].strip():
            raise ValueError("Each caption needs non-empty text")
        number(caption.get("start"), "caption start")
        number(caption.get("duration"), "caption duration", positive=True)
    return plan


def ensure_new_destination(drafts_root, name):
    destination = Path(drafts_root).expanduser().resolve() / name
    if destination.exists():
        raise FileExistsError(f"Draft already exists; choose a new version name: {destination}")
    return destination


def build(manifest, drafts_root):
    manifest = Path(manifest).resolve()
    plan = validate_plan(json.loads(manifest.read_text(encoding="utf-8")), manifest.parent)
    destination = ensure_new_destination(drafts_root, plan["name"])
    runtime = ROOT / "vendor/jianying-editor/scripts"
    sys.path.insert(0, str(runtime))
    os.environ["JY_SKILL_ROOT"] = str(runtime.parent)
    from jy_wrapper import JyProject
    import pyJianYingDraft as draft

    # No live application folder is chosen implicitly.
    project = JyProject(plan["name"], width=plan["width"], height=plan["height"],
                        drafts_root=str(destination.parent), overwrite=False)
    project._explicit_res = True
    project.script.fps = plan["fps"]
    marker = destination / "BUILD_INCOMPLETE.txt"
    marker.write_text("Draft construction is incomplete. Do not treat it as a finished project.\n", encoding="utf-8")
    copied = {}
    us = lambda seconds: round(seconds * 1_000_000)
    for clip in sorted(plan["clips"], key=lambda item: item["start"]):
        relative = clip["media"]
        if relative not in copied:
            source = resolve_asset(relative, manifest.parent)
            target = destination / "media" / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
            copied[relative] = target
        path = str(copied[relative])
        start, duration, source_start = us(clip["start"]), us(clip["duration"]), us(clip.get("source_start", 0))
        kind, track = clip["kind"], clip.get("track", KINDS[clip["kind"]])
        volume = clip.get("volume", 0 if kind == "video" else 1)
        if kind == "video":
            segment = project.add_clip(path, source_start=source_start, duration=duration,
                                       target_start=start, track_name=track)
            if segment is None:
                raise RuntimeError(f"Video import failed: {relative}")
            segment.volume = volume
        else:
            # The upstream audio helper starts at zero; use the underlying API for exact source ranges.
            project._ensure_track(draft.TrackType.audio, track)
            segment = draft.AudioSegment(path, draft.Timerange(start, duration),
                                         source_timerange=draft.Timerange(source_start, duration), volume=volume)
            project.script.add_segment(segment, track)
    for caption in sorted(plan.get("captions", []), key=lambda item: item["start"]):
        project.add_text_simple(caption["text"], start_time=us(caption["start"]),
                                duration=us(caption["duration"]), track_name="Subtitles")
    saved = project.save()
    portable_plan = json.loads(json.dumps(plan))
    for clip in portable_plan["clips"]:
        clip["media"] = "media/" + clip["media"]
    (destination / "production-plan.json").write_text(json.dumps(portable_plan, ensure_ascii=False, indent=2), encoding="utf-8")
    result = {"status": "draft_generated", "draft_path": saved["draft_path"],
              "clips": len(plan["clips"]), "captions": len(plan.get("captions", [])),
              "media_copied": len(copied), "application_open_verified": False,
              "exported": False, "note": "Open and inspect in the target JianYing installation before acceptance."}
    (destination / "build-report.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    marker.unlink()
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--drafts-root", type=Path, required=True)
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args()
    try:
        if args.validate_only:
            plan = validate_plan(json.loads(args.manifest.read_text(encoding="utf-8")), args.manifest.resolve().parent)
            ensure_new_destination(args.drafts_root, plan["name"])
            result = {"status": "plan_valid", "media_decoding_verified": False}
        else:
            with contextlib.redirect_stdout(sys.stderr):
                result = build(args.manifest, args.drafts_root)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except Exception as error:
        print(json.dumps({"status": "failed", "error": str(error)}, ensure_ascii=False), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
