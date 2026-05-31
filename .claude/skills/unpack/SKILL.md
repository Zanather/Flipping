---
name: unpack
description: Unpack FromSoftware mod files (.dcx/.bnd/.anibnd/.tae/.fmg/.param) with WitchyBND into editable folders/XML, ready for conflict-scan or hand-merging. Use when the user has packed mod files (e.g. c0000.anibnd.dcx) that need unpacking before merging.
---

# unpack

Drives WitchyBND to unpack mod files into the editable folder/XML form the rest
of the toolkit operates on.

## Prerequisite

WitchyBND must be installed and on PATH (or the user supplies its path). Check
with `witchybnd --help` (or `WitchyBND.exe`). If it is not available in this
environment, explain that WitchyBND is a Windows GUI/CLI tool the user runs
locally, and give them the exact commands to run there instead of failing.

## Steps

1. Identify the file(s) to unpack — e.g. `c0000.anibnd.dcx`, `regulation.bin`,
   a `.tae`, or a whole folder. Confirm the path with the user if ambiguous.

2. For a clean 3-way merge later, recommend unpacking **all three** versions
   into separate, clearly named folders: vanilla, mod A, mod B. Keep the vanilla
   unpack around as the base.

3. Run WitchyBND on each target:
   ```
   witchybnd "<path-to-file-or-folder>"
   ```
   WitchyBND unpacks in place, producing a sibling folder plus a
   `_witchy-*.xml` manifest (which records file order/IDs — do not hand-edit it
   carelessly, or repack will break).

4. Report where the unpacked folders landed, then point the user to:
   - `/conflict-scan` for anibnd/chrbnd/C0000 file merges, or
   - `/param-merge` for regulation.bin param CSVs (export from Smithbox first).

## Repacking

To repack after merging, run WitchyBND on the **unpacked folder** (it reads the
manifest and rebuilds the `.dcx`). Repack only the leaf you changed to avoid
whitespace/order churn.
