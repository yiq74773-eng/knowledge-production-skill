# Bundled JianYing runtime

Source snapshot of [luoluoluo22/jianying-editor-skill](https://github.com/luoluoluo22/jianying-editor-skill), from a locally maintained 1.5.0 installation. This is not asserted to be an exact upstream Git revision.

The basic supported entrypoint is `../../scripts/build_jianying.py`; see `../../references/jianying-runtime.md`. Source code and empty draft templates are included. Example media, local cloud-music/style indexes, caches and account state are excluded.

This distribution patches environment discovery to resolve its own bundled modules, requires an explicit draft root, and makes Windows UI automation imports optional for offline draft creation. The application itself and Python dependencies are not bundled.

Upstream wrapper license: [MIT](LICENSE). The included `scripts/vendor/pyJianYingDraft` has its own [Apache-2.0 license](scripts/vendor/pyJianYingDraft/LICENSE). See `../../THIRD_PARTY_NOTICES.md` for provenance and modifications.
