#!/usr/bin/env bash
# smoke.sh — drive both mod-merging-toolkit CLIs end-to-end against synthetic
# fixtures that exercise every conflict category, and assert on their output +
# exit codes. No game files needed: it fabricates vanilla/modA/modB inputs in a
# temp dir, runs param_delta.py and conflict_scan.py, and checks the results.
#
# Run from the toolkit root:   bash .claude/skills/run-mod-merging-toolkit/smoke.sh
# Exit 0 = both tools behaved exactly as expected; non-zero = a check failed.
set -uo pipefail

# Resolve the toolkit root from this script's location (skill dir is 3 levels deep).
SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SKILL_DIR/../../.." && pwd)"
SCRIPTS="$ROOT/scripts"
PY="${PYTHON:-python3}"

WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

fail=0
check() { # check <label> <expected-exit> <actual-exit> ; plus grep checks via env
  local label="$1" want="$2" got="$3"
  if [ "$want" != "$got" ]; then
    echo "  FAIL: $label — expected exit $want, got $got"; fail=1
  else
    echo "  ok  : $label (exit $got)"
  fi
}
grepcheck() { # grepcheck <label> <pattern> <file>
  if grep -qE "$2" "$3"; then echo "  ok  : $1"; else
    echo "  FAIL: $1 — pattern not found: $2"; fail=1; fi
}

# ----------------------------------------------------------------------------
echo "== Track A: param_delta.py (CSV 3-way merge) =="
# Columns: ID,Name,field0,field1  (no header row, Smithbox/DSMapStudio style).
# row 1000: A edits field0, B edits field1   -> auto-merge (disjoint)
# row 2000: A and B both set field0 differently -> FIELD CONFLICT
# row 3000: only A edits                      -> take A
# row 9001: both add same new ID, same data   -> clean
# row 9002: both add same new ID, diff data    -> ADD COLLISION
P="$WORK/params"; mkdir -p "$P"
cat > "$P/van.csv" <<'CSV'
1000,Sword,10,5
2000,Spear,20,8
3000,Axe,30,9
CSV
cat > "$P/a.csv" <<'CSV'
1000,Sword,99,5
2000,Spear,77,8
3000,Axe,30,123
9001,NewBow,1,1
9002,NewStaff,5,5
CSV
cat > "$P/b.csv" <<'CSV'
1000,Sword,10,55
2000,Spear,88,8
3000,Axe,30,9
9001,NewBow,1,1
9002,NewStaff,6,6
CSV

OUT="$WORK/merged.csv"; JSON="$WORK/params.json"
"$PY" "$SCRIPTS/param_delta.py" --vanilla "$P/van.csv" --a "$P/a.csv" --b "$P/b.csv" \
  --out "$OUT" --json "$JSON" > "$WORK/param.out" 2>&1
rc=$?
cat "$WORK/param.out" | sed 's/^/    /'
check "param_delta exits 1 (conflicts present)" 1 "$rc"
grepcheck "reports 1 add collision"  "ADD COLLISIONS \(1\)"   "$WORK/param.out"
grepcheck "reports 1 field conflict" "FIELD CONFLICTS \(1\)"  "$WORK/param.out"
grepcheck "auto-merged the disjoint row 1000" "id 9002" "$WORK/param.out"
grepcheck "merged CSV carries auto-merged row 1000" "^1000,Sword,99,55$" "$OUT"
grepcheck "merged CSV keeps conflict row 2000 at vanilla" "^2000,Spear,20,8$" "$OUT"
grepcheck "JSON written" '"field_conflicts"' "$JSON"

echo
echo "== Track A: clean case (no conflicts -> exit 0) =="
cat > "$P/b2.csv" <<'CSV'
1000,Sword,10,5
3000,Axe,30,9
CSV
"$PY" "$SCRIPTS/param_delta.py" --vanilla "$P/van.csv" --a "$P/van.csv" --b "$P/b2.csv" \
  > "$WORK/param2.out" 2>&1
check "param_delta exits 0 when no conflicts" 0 "$?"

# ----------------------------------------------------------------------------
echo
echo "== Track B: conflict_scan.py (unpacked-tree 3-way scan) =="
# Build three WitchyBND-style unpacked trees.
mk() { mkdir -p "$(dirname "$1")"; printf '%s' "$2" > "$1"; }
V="$WORK/vanilla"; A="$WORK/modA"; B="$WORK/modB"

# anim clip both mods change differently -> ANIMATION ID COLLISION
mk "$V/a000_003000.hkx" "vanilla-clip"
mk "$A/a000_003000.hkx" "modA-clip"
mk "$B/a000_003000.hkx" "modB-clip"
# file only A changed vs vanilla -> AUTO-RESOLVABLE (take A)
mk "$V/shared.bin" "v"; mk "$A/shared.bin" "A-changed"; mk "$B/shared.bin" "v"
# clean additions
mk "$A/onlyA.hkx" "x"; mk "$B/onlyB.hkx" "y"
# TAE both edit different animations -> mergeable per-animation
tae() { mk "$1" "<TAE><Animations><Animation ID=\"3000\">$2</Animation><Animation ID=\"5000\">$3</Animation></Animations></TAE>"; }
tae "$V/c0000.tae.xml" "<E>v3</E>" "<E>v5</E>"
tae "$A/c0000.tae.xml" "<E>A3</E>" "<E>v5</E>"   # A changed only anim 3000
tae "$B/c0000.tae.xml" "<E>v3</E>" "<E>B5</E>"   # B changed only anim 5000

JSON2="$WORK/scan.json"
"$PY" "$SCRIPTS/conflict_scan.py" --a "$A" --b "$B" --vanilla "$V" --json "$JSON2" \
  > "$WORK/scan.out" 2>&1
rc=$?
cat "$WORK/scan.out" | sed 's/^/    /'
check "conflict_scan exits 1 (overwrite conflicts present)" 1 "$rc"
grepcheck "flags the animation-ID collision" "a000_003000\.hkx" "$WORK/scan.out"
grepcheck "marks shared.bin auto-resolvable (take A)" "take A: shared\.bin" "$WORK/scan.out"
grepcheck "TAE detail says mergeable (different animations)" "mergeable" "$WORK/scan.out"
grepcheck "lists clean additions" "\+ onlyA\.hkx" "$WORK/scan.out"
grepcheck "JSON written" '"anim_id_collisions"' "$JSON2"

echo
if [ "$fail" = 0 ]; then echo "SMOKE PASSED — both tools behaved as expected."; else
  echo "SMOKE FAILED — see FAILs above."; fi
exit "$fail"
