"""Build a single-root skill ZIP and a plain-text entry for hosts without skill loading."""
import argparse
import hashlib
from pathlib import Path
import zipfile

REPO = Path(__file__).resolve().parents[1]
SKILL = REPO / "skills" / "knowledge-production"


def package(output):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    archive = output / "knowledge-production.zip"
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as result:
        for path in sorted(SKILL.rglob("*")):
            if path.is_file() and "__pycache__" not in path.parts and path.suffix != ".pyc":
                name = (Path("knowledge-production") / path.relative_to(SKILL)).as_posix()
                info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
                info.create_system = 3
                info.external_attr = 0o100644 << 16
                result.writestr(info, path.read_bytes(), compress_type=zipfile.ZIP_DEFLATED)
    sections = ["SKILL.md", "references/research.md", "references/production.md",
                "references/integrations.md", "references/portability.md", "vendor/text-cleanup/RULES.md",
                "vendor/text-cleanup/LICENSE", "LICENSE"]
    prompt = output / "knowledge-production-prompt.md"
    intro = "# 知识作品制作：普通对话入口\n\n以下为完整工作流和文案规则。请按需执行，不要因为读到制作指令就声称拥有文件、浏览器或剪映控制能力。用户观点和作品方向不清时先询问。文中的相对链接指向 ZIP 包；本文件不包含运行代码。\n\n"
    prompt.write_text(intro + "\n\n".join("<!-- " + part + " -->\n\n" + (SKILL / part).read_text(encoding="utf-8") for part in sections), encoding="utf-8", newline="\n")
    hashes = output / "SHA256SUMS.txt"
    hashes.write_text("\n".join(hashlib.sha256(path.read_bytes()).hexdigest() + "  " + path.name for path in (archive, prompt)) + "\n", encoding="utf-8", newline="\n")
    return archive


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=REPO / "dist")
    print(package(parser.parse_args().output))
