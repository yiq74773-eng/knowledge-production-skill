# Third-party components

## lieflat-less-ai-tone

- Source project (installation address): <https://github.com/larashero3-dotcom/lieflat-less-ai-tone>
- Included material: full local `SKILL.md` renamed to `vendor/text-cleanup/RULES.md`, supporting `RESEARCH.md`, and [original license](vendor/text-cleanup/LICENSE).
- Copyright (c) 2026 shiujan. MIT License.
- The snapshot came from the installed skill, not a verified upstream commit. The rule text is preserved; its exact bytes are recorded in the package manifest.

## jianying-editor-skill

- Source project: <https://github.com/luoluoluo22/jianying-editor-skill>
- Included material: Python runtime source and empty draft templates, from a locally maintained installation whose VERSION is 1.5.0. No exact upstream commit is claimed.
- Copyright (c) 2026 luoluoluo22. [MIT License](vendor/jianying-editor/LICENSE).
- Distribution modifications: self-contained environment bootstrap, explicit draft-root requirement, optional Windows UI import, and a separate non-overwriting relative-path plan adapter. Local installation may already contain changes relative to upstream.
- Not included: private projects, recordings, cached media, editor fonts/effect assets or cloud-music indexes.

## pyJianYingDraft

- Source project: <https://github.com/GuanYixuan/pyJianYingDraft>
- Included via the wrapper's vendored snapshot; exact original revision not established.
- [Apache License 2.0](vendor/jianying-editor/scripts/vendor/pyJianYingDraft/LICENSE), obtained from the upstream project's LICENSE on 2026-09-28.
- Modified `__init__.py`: GUI automation becomes optional on Windows for offline construction. Other changes may predate this distribution's local snapshot.

These licenses apply to their respective components. The generated work, user media, editor software and third-party media are not licensed by this file. Python/system dependencies are installed separately under their own licenses.
