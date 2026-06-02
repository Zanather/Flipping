# Elden Ring / FromSoftware Modding — Knowledge Base

A self-contained reference for merging FromSoft mods (Elden Ring, Dark Souls 3,
Sekiro). Covers file formats, tooling, merge workflows, and common pitfalls.
Written to be dropped into any AI model's context as a knowledge primer.

---

## Core Concepts

**FromSoftware games use packed binary archives.** Mods work by replacing files
inside these archives. When two mods replace the *same* file, one overwrites the
other — that's a mod conflict. Merging = combining both mods' changes so neither
is lost.

There are two independent conflict domains:
1. **Params** (gameplay data: weapon stats, spell effects, enemy HP) — stored in
   `regulation.bin`.
2. **Files** (animations, models, textures, behavior graphs) — stored in
   `.bnd`/`.dcx` archives like `c0000.anibnd.dcx`.

Most mod merges involve one or both.

---

## File Formats

### regulation.bin
- A DCX-compressed BND archive containing `.param` files.
- Each `.param` is a table: rows identified by integer **ID**, columns are typed
  fields (ints, floats, bools). Think of it as a spreadsheet per gameplay system.
- Key params: `EquipParamWeapon`, `SpEffectParam`, `AtkParam_Npc`,
  `EquipParamProtector`, `ReinforceParamWeapon`, `BulletParam`, etc.
- Tools export params to **CSV**: one row per entry, columns = ID, Name, field0,
  field1, ... (no header row in DSMapStudio/Smithbox exports; comma-delimited).

### .anibnd.dcx (Animation Bundle)
- DCX-compressed BND of animation-related files for a character.
- `c0000` = the player character. `c0000.anibnd.dcx` is the most commonly
  merged archive because moveset/combat mods all touch it.
- Contents:
  - **`.hkx` animation clips** — named `aXXX_YYYYYY.hkx` where XXX is a
    category and YYYYYY is the animation ID. These are Havok binary files
    containing the actual skeletal animation data.
  - **`.tae` / TimeActEvents** — define *when* gameplay events fire during an
    animation: hitbox activation, i-frame windows, sound effects, VFX triggers,
    cancel windows, parry windows, motion blur, etc. WitchyBND serializes these
    to readable `.tae.xml`. Each TAE file contains multiple **animations**, and
    each animation contains a list of **events** with timing data.
  - **Behavior `.hkx` / `.behbnd`** — the Havok behavior state graph that
    decides which animation plays based on game state (input, flags, conditions).
    This is the hardest part to merge — it's a complex state machine, not a flat
    data table.

### .chrbnd.dcx (Character Bundle)
- Contains the character's FLVER model, textures, and sometimes additional
  params. Less commonly conflicting than anibnd.

### .dcx (General)
- DCX is FromSoft's compression wrapper. Almost all game files are
  `something.dcx`. Tools handle compression/decompression transparently.

### Other mergeable formats
- **`.fmg`** — text/string tables (item descriptions, dialogue).
- **`.flver`** — 3D model data.
- **`.msgbnd`** — message bundles containing FMG files.
- **`.tpf`** — texture packs.

---

## Key Tools

### Smithbox (successor to DSMapStudio)
- The primary param editor. Opens `regulation.bin` directly.
- **Delta Param Patcher** — the modern merge approach. Diffs a modded
  `regulation.bin` against vanilla and shows only changed rows (highlighted
  green). You apply each mod's delta onto your base and resolve rows both
  touched. This is preferred over CSV export/import for in-GUI work.
- Can also export/import params as CSV for scripted merging.
- Repo: github.com/vawser/Smithbox

### WitchyBND (successor to Yabber)
- Unpacks and repacks FromSoft archive formats: `.dcx`, `.bnd`, `.bhd+bdt`,
  `.tae`, `.fmg`, `.param`, `.flver`, and more.
- Unpacking produces a folder + a `_witchy-*.xml` manifest file that records
  file order and internal IDs. **Do not hand-edit the manifest carelessly** — it
  controls repack behavior, and wrong IDs break the archive.
- TAE files are serialized to `.tae.xml` (readable XML with animation IDs and
  event definitions).
- To repack: run WitchyBND on the **unpacked folder** (not the original file).
  It reads the manifest and rebuilds the `.dcx`.
- Repo: github.com/ividyon/WitchyBND

### DSAnimStudio
- Viewer/editor for TAE events and animation previews. Essential for behavior
  graph conflicts and detailed TAE merging that goes beyond what text-diffing
  can handle.
- By Meowmaritus.

### Other useful tools
- **Yapped Rune Bear** — fast standalone param editor (lighter than Smithbox).
- **ERMM (Elden Ring Mods Merger)** — automated regulation.bin merger (less
  control than manual merging but handles simple cases).
- **hkxconv / FromSoftHKX** — Havok format conversion utilities for working
  with behavior/animation .hkx files outside of the game's native format.

---

## Merge Workflow — Params (regulation.bin)

### Mental model
Every mod's changes are a **delta against vanilla**. Merging two mods = applying
both deltas. Conflicts only exist where both deltas touch the same thing.

### Conflict categories
1. **Clean additions** — a mod adds new rows in an unused ID range. Zero
   conflict potential. This is why ID-range discipline matters.
2. **Single-mod edits** — only one mod changed a given row. Take it as-is.
3. **Disjoint field edits** — both mods edited the same row, but different
   fields (e.g., mod A changed attack power, mod B changed weight). These
   combine cleanly — apply both field changes onto the vanilla base.
4. **Same-field conflicts** — both mods set the *same* field of the *same* row
   to different values. This is the only true conflict. You must pick one value
   or create a compromise.
5. **Add-ID collisions** — both mods added a new row at the same ID with
   different data. Re-ID one mod's addition, or pick a winner.

### Workflow
1. Export the same param from vanilla, mod A, and mod B as CSV (Smithbox: Param
   Editor → select param → export CSV).
2. Run 3-way analysis (scripted or manual diff).
3. Auto-merge categories 1-3. Manually resolve categories 4-5.
4. Import the merged CSV back into Smithbox and save the merged regulation.bin.

### In Smithbox directly
Use the Delta Param Patcher: load vanilla as base, apply mod A's delta, then
apply mod B's delta. Rows highlighted green were changed. Where both mods
changed the same row, inspect field-by-field.

---

## Merge Workflow — Files / C0000 / Animations

### Mental model
Two mods that ship modified versions of the same file (e.g., both have
`c0000.anibnd.dcx`) will overwrite each other. Merging means unpacking both,
identifying what each mod actually changed vs vanilla, and combining those
changes into one repacked archive.

### Conflict categories
1. **Animation ID collisions** — both mods ship `aXXX_YYYYYY.hkx` (same
   filename) with different content. One silently overwrites the other if not
   caught. Fix: re-ID one mod's clip *and* update every reference to it in both
   the behavior graph and TAE, or one mod's animation is lost.
2. **TAE conflicts** — both mods edited the same `.tae` file. This can be
   further broken down:
   - **Different animations edited** — mod A changed animation 3000's events,
     mod B changed animation 5000's events, but both are in the same `.tae`
     file. This is **mergeable** at animation granularity (copy both animation
     entries into the merged TAE).
   - **Same animation edited** — both mods changed the events for animation
     3000. True conflict. Must be resolved by hand (usually in DSAnimStudio)
     by comparing the event timings and deciding which events to keep.
3. **Behavior graph conflicts** — both mods edited the Havok behavior state
   graph (`.hkx` in the behbnd). This is the hardest to merge because it's a
   complex state machine with states, transitions, and conditions. Usually
   requires DSAnimStudio and deep understanding of the behavior tree. Cannot
   be reliably text-merged.
4. **Auto-resolvable** — a file exists in both mods' unpacked trees but only
   one actually changed it vs vanilla. Take the changed version.
5. **Clean additions** — one mod adds files the other doesn't have at all
   (e.g., entirely new animation clips in unused ID ranges). Copy them in, no
   conflict.

### Workflow
1. WitchyBND-unpack all three versions (vanilla, mod A, mod B) of the target
   archive (e.g., `c0000.anibnd.dcx`) into separate folders.
2. Scan for collisions (compare file hashes across the three trees).
3. Work the results top-down by severity:
   - Fix animation ID collisions first (re-ID + update references).
   - Merge TAE conflicts (combine animation entries or hand-merge events).
   - Copy auto-resolvable and clean additions.
   - Address behavior graph conflicts last (hardest, may need DSAnimStudio).
4. Repack the merged folder with WitchyBND. Only repack the leaf you changed
   to avoid introducing whitespace/order churn from the manifest.

---

## The Golden Rules

1. **Always keep a vanilla copy as the 3-way base.** Without it, every
   difference between two mods looks like a conflict. With it, you can
   distinguish "both changed this" (real conflict) from "only one changed
   this" (auto-resolvable).

2. **ID-range discipline prevents most conflicts.** When a mod *adds* new rows
   (params) or new animations (clips), it should use an unused ID range. Clean
   additions in disjoint ranges never collide. Conflicts almost always come from
   two mods editing the *same* existing ID.

3. **Merge at the finest granularity possible.** Don't stop at "these two files
   conflict." For params, go field-by-field. For TAE, go animation-by-animation.
   Many apparent "file conflicts" decompose into non-overlapping changes that
   merge cleanly once you look inside.

4. **Behavior graph merges are the hard ceiling.** Everything else (params, TAE,
   animation clips, models, textures) can be diffed and merged with text/data
   tools. Behavior graphs are complex state machines that resist automated
   merging. Budget time for these and use DSAnimStudio.

5. **Test after every merge.** Load the game, verify the merged animations play
   correctly, check that param changes are reflected in-game, and watch for
   silent breakage (animations that play the wrong clip, hitboxes that don't
   activate, missing sounds).

---

## Scripted Tooling (mod-merging-toolkit)

### param_delta.py
Field-level 3-way merge for param CSVs. Auto-merges disjoint field edits, flags
same-field conflicts and add-ID collisions. Writes a merged CSV where conflicts
stay at vanilla (never guessed). Supports single-param or whole-regulation
(directory) mode. Pure Python stdlib, no dependencies.

```bash
# Single param
python3 param_delta.py --vanilla v.csv --a A.csv --b B.csv --out merged.csv

# Whole regulation (dirs of per-param CSVs)
python3 param_delta.py --vanilla van/ --a A/ --b B/ --out-dir merged/
```

### conflict_scan.py
3-way collision detection for WitchyBND-unpacked trees. Reports animation-ID
collisions, TAE conflicts (with per-animation breakdown showing which specific
animations each mod changed), overwrite conflicts, auto-resolvable diffs, and
clean additions. Pure Python stdlib.

```bash
python3 conflict_scan.py \
    --a modA/c0000-anibnd --b modB/c0000-anibnd --vanilla vanilla/c0000-anibnd
```

---

## Common Pitfalls

- **Forgetting to update references after re-IDing an animation.** If you
  rename `a000_003000.hkx` to `a000_903000.hkx`, you must also update the
  behavior graph and TAE entries that reference animation 3000 to point to
  903000, or the game plays the wrong (or no) animation.
- **Editing the WitchyBND manifest XML carelessly.** The `_witchy-*.xml` file
  controls file order and internal IDs during repack. Changing IDs or removing
  entries breaks the archive.
- **Merging without a vanilla base.** Every file that differs between two mods
  looks like a conflict, even files one mod didn't touch. Always use 3-way.
- **Assuming file-level conflict = unresolvable.** Two mods editing the same
  `.tae` file often edited *different animations* inside it — that's mergeable.
  Two mods editing the same param row often edited *different fields* — also
  mergeable. Always drill down.
- **Silent overwrites.** If you just drop both mods into the game folder without
  merging, one mod's files silently overwrite the other's. The game won't crash
  — it just uses whichever file was written last, and the other mod's changes
  are gone.
