# Public machinery development

This repository contains reusable machinery, not an Obsidian vault.

- Keep framework files inert under `framework/`; do not install them into this
  checkout's `.opencode/` or change the owner's global configuration.
- Never bring private notes, exports, settings, credentials, transcripts,
  backups, vault symlinks, or private-derived fixtures into this repository.
  Use wholly synthetic fixtures. Ignore rules are not a secrecy boundary.
- Follow PLAN.md's phase dependencies and owner approval checkpoints. Record
  actual results separately from proposals; a static test is not runtime proof.
- Preserve upstream notices and extend the file/revision adaptation map.
- Use Python's standard library for the planned CLIs. Run the narrow relevant
  checks; current distribution check: `python3 -m unittest discover -s tests -v`.
- Distribution is an approved per-file copy/merge, never a recursive vault
  copy, reverse sync, overwrite of local instructions, or automatic publication.
- Keep credentials and effective-config dumps out of tool output. Inspect only
  a sanitized allowlisted summary when runtime inspection is approved.
