"""Validate portable authored references, source syntax and package content without extra packages."""
import ast
import json
from pathlib import Path
import re
import sys

REPO = Path(__file__).resolve().parents[1]
SKILL = REPO / "skills/knowledge-production"


def validate():
    issues = []
    content = (SKILL / "SKILL.md").read_text(encoding="utf-8")
    if not content.startswith("---\n") or "name: knowledge-production" not in content.split("---", 2)[1]:
        issues.append("Invalid skill frontmatter/name")
    for file in SKILL.rglob("*.py"):
        try:
            ast.parse(file.read_text(encoding="utf-8"), filename=str(file))
        except (SyntaxError, UnicodeError) as error:
            issues.append(str(error))
    # Vendor research keeps its upstream provenance links. Validate authored navigation separately.
    authored = [SKILL / "SKILL.md", SKILL / "THIRD_PARTY_NOTICES.md", *list((SKILL / "references").glob("*.md"))]
    for file in authored:
        text = file.read_text(encoding="utf-8")
        for target in re.findall(r"\]\(([^)]+)\)", text):
            if "://" in target or target.startswith("#"):
                continue
            if not (file.parent / target.split("#")[0]).is_file():
                issues.append(f"Broken reference: {file.name} -> {target}")
    blocked = re.compile(r"C:[\\/]Users[\\/]25601|/Users/25601|gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{20,}|-----BEGIN (?:RSA |OPENSSH )?PRIVATE KEY-----")
    for file in SKILL.rglob("*"):
        if file.is_file() and file.suffix in (".py", ".md", ".json", ".yaml", ".txt"):
            if blocked.search(file.read_text(encoding="utf-8")):
                issues.append("Private path or credential pattern: " + str(file.relative_to(SKILL)))
    required = ["vendor/text-cleanup/RULES.md", "vendor/text-cleanup/LICENSE", "vendor/jianying-editor/LICENSE",
                "vendor/jianying-editor/scripts/vendor/pyJianYingDraft/LICENSE", "scripts/build_jianying.py",
                "requirements-video.txt", "LICENSE"]
    for name in required:
        if not (SKILL / name).is_file():
            issues.append("Missing bundled requirement: " + name)
    return issues


if __name__ == "__main__":
    problems = validate()
    print(json.dumps({"status": "passed" if not problems else "failed", "issues": problems}, ensure_ascii=False, indent=2))
    sys.exit(bool(problems))
