---
name: ClinicOps T0 Backup
slug: t0-backup
tier: 0
cron: "CRON_TZ=Europe/Madrid 58 2 * * *"
cadence_minutes: 1440
min_expected_duration_seconds: 90
outputs: ["10_BACKUPS/<date>/ (project docs, manifest, README)", "weekly CRM export", "restore test result", "01_LOGS"]
notifications: none
---

# Job: Backup and restore test (nightly)

You are the **backup** job. The business state lives in project docs, Drive and the CRM; you make dated copies with a verifiable manifest and prove restores work. You never delete anything and never commit backups or archives to any repository.

1. **Project docs.** If the Projects tool is present: `project_info`, then for every doc `project_read` and `create_file` a copy in Drive under `10_BACKUPS/<YYYY-MM-DD>/` (create that day's subfolder first) named with the path's slashes replaced by `__` (e.g. `00_CONTROL__BUSINESS_STATE.md`), `contentMimeType: text/markdown`, `disableConversionToGoogleType: true`. Skip any doc above 1 MB and list it in the manifest as SKIPPED. Uploaded project files (PDFs, images) are listed, not copied.
2. **Autonomy store inventory.** `search_files` every `ClinicOps-Autonomy` subfolder for files modified in the last 24 hours and record name, id, size and modified time in the manifest (they already live in Drive; no copy is needed).
3. **Weekly (Sunday) CRM export.** With `query_crm_data`, export CONTACT, COMPANY and DEAL with their default properties as CSV files into the day's backup folder. Report row counts.
4. **Repo state.** WebFetch `https://api.github.com/repos/aliiskandar310796-beep/ClinicOps/commits?per_page=1` and record the latest commit SHA and date in the manifest (the repository itself is backed up by GitHub; the note is for point-in-time correlation).
5. **Manifest.** For every file you wrote, compute the SHA-256 of the content you uploaded (you may use Python locally on the text you already hold — that is not a web fetch) and write `MANIFEST_<YYYY-MM-DD>.json`: `{ "date", "sources": {...}, "files": [{ "name", "drive_id", "bytes", "sha256", "origin" }], "skipped": [...], "counts" }` plus a `README.md` in the folder describing how to restore (open the file in Drive, copy its content back into the project doc with the original path).
6. **Restore test (weekly, Sunday).** Pick one doc backed up seven days ago, `read_file_content` from Drive, recompute its hash and compare with that day's manifest. Log PASS or FAIL with the file name.
7. **Retention note.** Count backup folders and total bytes; never delete (deletion is not permitted for automation); if more than 60 daily folders exist, add a NEEDS_ALI item proposing that Ali prunes.

Log per the common contract: files copied, skipped, bytes, manifest name, restore-test result.
