---
name: run-mod-merging-toolkit
description: Run, build, smoke-test, and drive the FromSoftware mod-merging-toolkit CLIs (param_delta.py, conflict_scan.py). Use when asked to run the toolkit, verify the merge scripts work, smoke-test a change to param_delta/conflict_scan, or see the tools produce a real report.
---

# Run: mod-merging-toolkit

Two pure-stdlib Python 3 CLIs that do 3-way merge analysis for FromSoft mods:

- `scripts/param_delta.py` — field-level merge of `regulation.bin` param CSV
  exports (vanilla / mod A / mod B). Auto-merges disjoint field edits, flags
  same-field conflicts + add-ID collisions, can write a merged CSV.
- `scripts/conflict_scan.py` — collision scan of two WitchyBND-unpacked trees
  (e.g. `c0000.anibnd`) against a vanilla base. Flags anim-ID collisions, TAE
  conflicts (with per-animation breakdown), auto-resolvables, clean additions.

There is no GUI and no server — these are command-line tools. The way to drive
them is the **smoke harness**, which fabricates synthetic vanilla/modA/modB
inputs exercising every conflict category, runs both tools, and asserts on
their output and exit codes. No game files required.

**Paths below are relative to `mod-merging-toolkit/`** (the unit root). The
driver lives at `.claude/skills/run-mod-merging-toolkit/smoke.sh`.

## Prerequisites

Python 3.8+. Nothing to install — both scripts are stdlib-only.

```bash
python3 --version   # 3.11.15 here; any 3.8+ works
```

`witchybnd` (the unpack/repack step that *produces* the inputs) is a Windows
tool and is **not** needed to run these scripts — they operate on already-unpacked
folders and exported CSVs. On this Linux container it is not on PATH; that's
expected and does not block the toolkit.

## Run (agent path) — the smoke harness

```bash
bash .claude/skills/run-mod-merging-toolkit/smoke.sh
```

Exit `0` = both tools behaved exactly as expected (every category detected,
exit codes correct, merged CSV/JSON content verified). Non-zero = a check
failed, with `FAIL:` lines naming what broke. This is the fastest way to
confirm a change to either script didn't regress behavior — run it after any
edit to `param_delta.py` or `conflict_scan.py`.

The harness builds its fixtures in a temp dir and cleans up on exit; it leaves
the repo untouched.

## Run (real inputs) — driving the tools directly

Track A (params) — three CSV exports of the *same* param (no header row;
`ID,Name,field0,field1,...`):

```bash
python3 scripts/param_delta.py \
    --vanilla vanilla/EquipParamWeapon.csv \
    --a modA/EquipParamWeapon.csv \
    --b modB/EquipParamWeapon.csv \
    --out merged.csv --json report.json
```

Whole regulation: point `--vanilla/--a/--b` at folders of per-param CSVs and
use `--out-dir merged/` instead of `--out`.

Track B (files) — three WitchyBND-unpacked folders:

```bash
python3 scripts/conflict_scan.py \
    --a modA/c0000-anibnd --b modB/c0000-anibnd \
    --vanilla vanilla/c0000-anibnd --json scan.json
```

Both print a human report to stdout and write JSON with `--json`.

## Test

There is no separate unit-test suite; the smoke harness above is the test.
Syntax is also checked on every session start by `.claude/hooks/check-tools.sh`
(it runs `python3 -m py_compile` on both scripts).

## Gotchas

- **Exit 1 is success, not failure, when conflicts exist.** Both tools exit
  non-zero when they find real conflicts (handy for CI gating). The smoke
  harness *expects* exit 1 on its conflict fixtures and exit 0 on the clean
  fixture — don't "fix" a passing run that shows exit 1.
- **CSVs have no header row.** Smithbox/DSMapStudio exports are bare
  `ID,Name,field0,...`. A stray header line is skipped (non-integer ID), but
  don't add one expecting it to be used.
- **`conflict_scan` needs `--vanilla` to be useful.** Without the 3-way base,
  *every* file that differs between A and B is reported as a conflict, and the
  auto-resolvable / TAE-per-animation breakdown is empty.
- **`param_delta` never guesses a conflict winner.** Conflicting rows are
  written to the merged CSV at their *vanilla* value; you resolve those by hand
  in Smithbox. Auto-merged (disjoint) rows are fully combined.
- **TAE per-animation detail only fires for `.tae.xml`** (WitchyBND's
  serialized form) with a vanilla base present. Raw `.tae` binaries fall back
  to file-level comparison.
- **Multi-unit repo.** This skill covers only `mod-merging-toolkit/`. The repo
  root is an unrelated RuneLite plugin (Gradle/Java) and there's a separate
  `d2r-build-verify/` C++ tree — neither is driven by this skill.

## Troubleshooting

- `--a is a dir but --b is not` (or similar) — directory mode and single-file
  mode can't be mixed. Use dirs+`--out-dir` for whole-regulation, or
  files+`--out` for one param.
- `no *.csv files found in --a / --b dirs` — directory mode found no matching
  `*.csv`; check the export paths.
- Smoke `FAIL:` lines after editing a script — the change altered output
  wording or exit behavior the assertions depend on; reconcile the script and
  the `grepcheck` patterns in `smoke.sh`.
