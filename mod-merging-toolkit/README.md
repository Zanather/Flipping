# FromSoftware Mod-Merging Toolkit

Helper tooling + workflow notes for merging FromSoft mods (Elden Ring / DS3 /
Sekiro style) with **Smithbox** + **WitchyBND**. The binary tools do the heavy
lifting; the scripts here handle the *bookkeeping* — telling you exactly what
collides so you only hand-merge what actually conflicts.

> Lives inside the `Flipping` repo only because that's the pushable remote.
> It's fully self-contained under `mod-merging-toolkit/` and unrelated to the
> RuneLite plugin.

## Two tracks

| Track | What conflicts | Best tool | Helper here |
|-------|----------------|-----------|-------------|
| **Params** (`regulation.bin`) | Same param row edited by 2 mods | Smithbox **Delta Param Patcher** | `scripts/param_delta.py` |
| **Files** (anibnd / chrbnd / C0000) | Same file or animation ID in 2 mods | WitchyBND + hand-merge | `scripts/conflict_scan.py` |

---

## Track 1 — regulation.bin (params)

On current Smithbox, prefer the **Delta Param Patcher** over CSV export/import.
It diffs a modded `regulation.bin` against vanilla and shows only the changed
rows (highlighted green), then patches those deltas onto your base. That makes
merging two mods a matter of applying each mod's delta and resolving rows that
both touched.

Rule of thumb:
- **Clean additions** (a mod only adds rows in an unused ID range) → apply the
  delta, zero conflicts.
- **Same row, different fields** → usually combinable field-by-field.
- **Same row, same field, different values** → a real conflict; you decide.

Keep mods in disjoint ID ranges wherever a mod *adds* rows — that's what makes
additions clean. See sources at the bottom for full Smithbox merge tutorials.

### param_delta.py — field-level delta analysis

Smithbox's Delta Param Patcher merges great in the GUI but gives you no
written, diffable record of *what* two mods fight over. This script does. Export
the same param from vanilla, mod A, and mod B to CSV, then:

```text
python scripts/param_delta.py --vanilla v.csv --a A.csv --b B.csv --out merged.csv
```

It works at the **field** level, in the Delta-Patcher spirit (everything is a
delta vs vanilla):

- **Auto-merged** — A and B edit *different* fields of the same row. Not a
  conflict; the script combines both deltas onto the vanilla base.
- **Single-mod edits / clean additions** — only one mod touched it; applied as-is.
- **Field conflicts** — both mods set the *same* field to *different* values.
  The only thing you actually have to resolve by hand.
- **Add collisions** — both mods add the same new row ID with different data
  (re-ID one, or pick a winner).

`--out` writes a merged CSV with every clean/auto-mergeable change applied;
conflicting rows are kept at their **vanilla** value (never silently guessed)
so you resolve just those in Smithbox. Point `--a/--b/--vanilla` at directories
of per-param CSVs (with `--out-dir`) to process a whole regulation at once.
Non-zero exit when real conflicts exist.

## Track 2 — WitchyBND files & C0000 merges

`c0000` is the player. The container that causes "C0000 merge" headaches is
`c0000.anibnd.dcx`:

- **`aXXX_YYYYYY.hkx`** — the Havok animation clips.
- **`*.tae` / `*.tae.xml`** — TimeActEvents: when hitboxes, i-frames, sounds,
  and cancel windows fire. WitchyBND unpacks TAE to readable XML.
- **behavior `.hkx` / behbnd** — the state graph choosing which clip plays.
  This is the hard part; graph conflicts need **DSAnimStudio**, not text merge.

### Workflow

```text
1. WitchyBND-unpack vanilla, mod A, and mod B:
     witchybnd c0000.anibnd.dcx        ->  c0000-anibnd/
2. Scan for collisions:
     python scripts/conflict_scan.py \
         --a  modA/c0000-anibnd \
         --b  modB/c0000-anibnd \
         --vanilla  vanilla/c0000-anibnd \
         --json report.json
3. Resolve what it flags:
     - ANIMATION ID COLLISIONS -> re-ID one side's clip AND update every
       reference to it (behavior graph + TAE) so nothing dangles.
     - TAE CONFLICTS           -> diff the two .tae.xml, merge the events.
     - AUTO-RESOLVABLE         -> only one mod changed it; take that side.
     - CLEAN ADDITIONS         -> new clips from one mod; copy them in.
4. Repack the merged folder with WitchyBND.
```

### Why `--vanilla` matters

Without a base, *every* file that differs between the two mods looks like a
conflict — including files one mod simply didn't touch. With the vanilla tree
as a 3-way base, the scanner separates real "both changed it" conflicts from
"only one mod changed it" cases it can auto-resolve. Always pass `--vanilla`.

## conflict_scan.py

Pure-stdlib Python 3. Hashes every file in each tree and reports:

- **Overwrite conflicts** — same relative path, both mods changed it vs vanilla.
- **Animation ID collisions** — `aXXX_YYYYYY.hkx` present in both, differing
  content (the classic "both mods used the same free ID" break).
- **TAE conflicts** — TimeActEvents files both mods edited.
- **Auto-resolvable** — shared path, but only one mod differs from vanilla.
- **Clean additions** — files one mod adds that the other lacks.

Exit code is non-zero when real conflicts exist, so it drops cleanly into a
skill or CI check. Run `python scripts/conflict_scan.py -h` for flags.

## Roadmap

- Custom Claude Code skills: `/unpack`, `/conflict-scan`, `/param-merge`
  (wrappers so you run the whole flow by slash command). **Next.**
- SessionStart hook to verify WitchyBND + Python are on PATH.
- TAE-level parsing in `conflict_scan` (which animation/event entries collide,
  not just which files).

## Sources

- [How to Merge/Update Params With Smithbox (guide)](https://www.scribd.com/document/1019963147/How-to-Merge-update-Params-With-Smithbox-1)
- [How to merge regulation.bin & param editing with Smithbox (Nexus forum)](https://forums.nexusmods.com/topic/13496434-how-to-merge-regulationbin-files-and-do-param-editing-with-smithbox/)
- [Merge regulation.bin without CSV — Smithbox issue #156](https://github.com/vawser/Smithbox/issues/156)
- [Installing & merging regulation.bin mods/CSVs (Elden Ring Nexus)](https://www.nexusmods.com/eldenring/images/2651)
