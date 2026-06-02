---
name: param-merge
description: Field-level 3-way merge analysis of two FromSoft regulation.bin param CSV exports against vanilla (Smithbox Delta Param Patcher spirit). Auto-merges disjoint field edits, flags same-field conflicts and add-ID collisions, and can write a merged CSV. Use when merging regulation.bin / param mods.
---

# param-merge

Wraps `mod-merging-toolkit/scripts/param_delta.py` to merge param CSV exports.

## Prerequisite

The user needs CSV exports of the **same** param(s) from three sources: vanilla,
mod A, and mod B. In Smithbox: Param Editor → select the param → export to CSV.
For a whole regulation, export each param into a per-source directory and match
filenames across the three.

## Steps

1. Collect the paths (ask only for what's missing):
   - **Vanilla** CSV or directory (the delta base — strongly recommended).
   - **Mod A** CSV or directory.
   - **Mod B** CSV or directory.
   Decide single-param vs directory mode from whether they point at files or dirs.

2. Run (single param):
   ```bash
   python3 mod-merging-toolkit/scripts/param_delta.py \
       --vanilla "<V>" --a "<A>" --b "<B>" \
       --out /tmp/merged.csv --json /tmp/param_report.json
   ```
   Or whole regulation (directories):
   ```bash
   python3 mod-merging-toolkit/scripts/param_delta.py \
       --vanilla "<V>/" --a "<A>/" --b "<B>/" --out-dir /tmp/merged/
   ```

3. Summarize, emphasizing:
   - **Field conflicts** — both mods set the *same* field to different values.
     This is the only thing the user must resolve by hand (in Smithbox).
   - **Add collisions** — both add the same new row ID with different data;
     re-ID one or pick a winner.
   - **Auto-merged / single-mod edits / clean additions** — applied
     automatically; no action needed.

4. Explain the merged CSV: clean and auto-mergeable changes are applied;
   conflicting rows are kept at their **vanilla** value (never guessed), so the
   user resolves only those, then re-imports the CSV in Smithbox.

Exit code is non-zero when real conflicts exist.
