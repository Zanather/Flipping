# Quickstart — merging two mods, end to end

A practical run-through. Two tracks; most merges need both.

## 0. One-time setup
- Have **Smithbox** and **WitchyBND** installed locally (Windows).
- Have **Python 3** for the scripts here.
- Keep a **vanilla** copy of the files you're merging — it's the base that turns
  "everything looks different" into "here's the one thing that actually conflicts".

---

## Track A — regulation.bin (params)

1. **Export CSVs** from Smithbox (Param Editor → pick the param → export CSV) for
   the *same* param from three sources, into clearly named files:
   `vanilla/EquipParamWeapon.csv`, `modA/EquipParamWeapon.csv`, `modB/...`.
   (For a whole regulation, export each param into per-source folders.)

2. **Analyze + auto-merge:**
   ```bash
   python3 mod-merging-toolkit/scripts/param_delta.py \
       --vanilla vanilla/EquipParamWeapon.csv \
       --a modA/EquipParamWeapon.csv \
       --b modB/EquipParamWeapon.csv \
       --out merged.csv
   ```
   Whole regulation: point `--vanilla/--a/--b` at the folders, add `--out-dir merged/`.

3. **Read the report.** Everything auto-merges except:
   - **FIELD CONFLICTS** — both mods set the same field differently. Decide a winner.
   - **ADD COLLISIONS** — both added the same new row ID. Re-ID one, or pick one.

4. **Resolve + import.** `merged.csv` already has all the safe changes; conflicting
   rows are left at vanilla. Fix just those, then import `merged.csv` back into
   Smithbox and save the merged `regulation.bin`.

> In Smithbox itself you can also do this live with the **Delta Param Patcher**
> (it highlights changed rows green). The script gives you the written,
> diff-able record the GUI doesn't.

---

## Track B — C0000 / anibnd (files & animations)

1. **Unpack all three** with WitchyBND (vanilla, mod A, mod B):
   ```bash
   witchybnd c0000.anibnd.dcx      # produces c0000-anibnd/ next to it
   ```

2. **Scan for collisions:**
   ```bash
   python3 mod-merging-toolkit/scripts/conflict_scan.py \
       --a   modA/c0000-anibnd \
       --b   modB/c0000-anibnd \
       --vanilla vanilla/c0000-anibnd
   ```

3. **Work the report, top to bottom:**
   - **ANIMATION ID COLLISIONS** — both mods shipped the same `aXXX_YYYYYY.hkx`.
     Re-ID one mod's clip *and* update its references (behavior graph + TAE) so
     nothing dangles, or one silently overwrites the other.
   - **TAE PER-ANIMATION DETAIL** — for each conflicting `.tae.xml`:
     - *mergeable* (mods edited different animations) → copy both animations' events together.
     - *CONFLICT animations* → open those animations in **DSAnimStudio** and merge the events by hand.
   - **AUTO-RESOLVABLE / CLEAN ADDITIONS** → take the indicated side / copy in. No thinking required.

4. **Repack** the merged folder with WitchyBND (run it on the unpacked folder;
   it rebuilds the `.dcx` from the `_witchy-*.xml` manifest). Repack only the
   leaf you changed.

---

## Slash-command shortcuts (inside a Claude Code session)
- `/unpack` — drive WitchyBND unpack/repack.
- `/param-merge` — Track A.
- `/conflict-scan` — Track B.
Just type the command and answer the prompts; you don't need to remember flags.

## The one rule that prevents most conflicts
When a mod *adds* rows or animations, keep it in an **unused ID range**. Clean
additions never collide — conflicts almost always come from two mods editing the
*same* ID. Both scripts call clean additions out separately so you can confirm
a mod stayed in its lane.
