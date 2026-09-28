"""Copy the complete skill to a host's skills directory; never overwrite an installation."""
import argparse
from pathlib import Path
import shutil
import sys

SOURCE = Path(__file__).resolve().parents[1] / "skills" / "knowledge-production"


def install(destination):
    destination = Path(destination).expanduser().resolve()
    target = destination / "knowledge-production"
    if target.exists():
        raise FileExistsError(f"Already installed: {target}. Back it up and choose a new destination.")
    if destination.is_relative_to(SOURCE.resolve()):
        raise ValueError("Destination cannot be inside the source package")
    shutil.copytree(SOURCE, target, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    return target


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--agent", choices=("codex", "claude", "generic"), default="generic")
    parser.add_argument("--destination", type=Path, help="Parent skills directory, not the final skill folder")
    args = parser.parse_args()
    destination = args.destination
    if destination is None:
        if args.agent == "generic":
            parser.error("Generic hosts need --destination pointing to their skills directory")
        destination = Path.home() / (".agents" if args.agent == "codex" else ".claude") / "skills"
    try:
        print(install(destination))
        return 0
    except (OSError, ValueError) as error:
        print(str(error), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
