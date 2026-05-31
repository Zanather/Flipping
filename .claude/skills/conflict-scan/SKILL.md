---
name: conflict-scan
description: Scan two WitchyBND-unpacked FromSoft mod trees (e.g. c0000.anibnd) for merge conflicts — animation-ID collisions, TAE conflicts, overwrite conflicts — using vanilla as a 3-way base. Use when the user wants to merge two file-based mods (anibnd, chrbnd, C0000) and needs to know what collides before repacking.
---

# conflict-scan

Wraps `mod-merging-toolkit/scripts/conflict_scan.py` to find collisions between
two WitchyBND-unpacked mod folders.

## Steps

1. Determine the three paths. Ask the user only for whatever they didn't supply
   in the invocation:
   - **Mod A dir** (required) — a WitchyBND-unpacked folder, e.g. `modA/c0000-anibnd`.
   - **Mod B dir** (required) — the other mod's matching unpacked folder.
   - **Vanilla dir** (strongly recommended) — the unpacked vanilla version, used
     as the 3-way base. Without it, every difference looks like a conflict.
   If the user hasn't unpacked yet, point them at the `/unpack` skill first.

2. Run:
   ```bash
   python3 mod-merging-toolkit/scripts/conflict_scan.py \
       --a "<A>" --b "<B>" --vanilla "<VANILLA>" --json /tmp/conflict_report.json
   ```
   Omit `--vanilla` only if the user has no vanilla tree.

3. Summarize the report in plain language, prioritizing:
   - **Animation ID collisions** — both mods ship the same `aXXX_YYYYYY.hkx`
     with different content. One must be re-IDed and its references (behavior
     graph + TAE) updated, or it gets silently overwritten.
   - **TAE conflicts** — both edited the same TimeActEvents; diff the `.tae.xml`.
   - **Overwrite conflicts** — other files both changed.
   - **Auto-resolvable / clean additions** — note these are safe, no action.

4. If there are zero conflicts, say so clearly — the merge is mechanical.

Exit code is non-zero when real conflicts exist.
