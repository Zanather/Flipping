#!/usr/bin/env python3
"""
param_delta.py — field-level 3-way merge analysis for FromSoftware params.

Built around the Smithbox **Delta Param Patcher** model: every change is a
delta against vanilla. Give it three CSV exports of the *same* param
(EquipParamWeapon, SpEffectParam, ...) — vanilla, mod A, mod B — and it reports,
per row and per field, what each mod actually changed and where they truly
collide.

The key win over eyeballing diffs: if mod A edits field 5 of row 1000 and mod B
edits field 9 of the *same* row, that is NOT a conflict — it's two independent
deltas that combine cleanly. Only when both mods change the *same* field to
*different* values is it a real conflict you must resolve by hand.

CSV format (DSMapStudio / Smithbox export): comma-delimited, one row per line,
columns = ID, Name, field0, field1, ...  (no header row).

Single param:
    python param_delta.py --vanilla v.csv --a A.csv --b B.csv [--out merged.csv]

Whole regulation (directories of per-param CSVs, matched by filename):
    python param_delta.py --vanilla van/ --a A/ --b B/ --out-dir merged/

Pure stdlib. Exit code is non-zero when real conflicts exist.
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path

Row = list[str]            # full column list: [ID, Name, f0, f1, ...]
Param = dict[int, Row]     # row id -> columns


def load_param(path: Path) -> Param:
    out: Param = {}
    with path.open(newline="", encoding="utf-8-sig") as fh:
        for cols in csv.reader(fh):
            if not cols or not cols[0].strip():
                continue
            try:
                rid = int(cols[0])
            except ValueError:
                # Skip a stray header row (non-integer ID) gracefully.
                continue
            out[rid] = cols
    return out


def changed_cols(base: Row, other: Row) -> set[int]:
    """Column indices (>=1, i.e. Name + fields) that differ between rows."""
    n = max(len(base), len(other))
    diff = set()
    for i in range(1, n):
        bv = base[i] if i < len(base) else ""
        ov = other[i] if i < len(other) else ""
        if bv != ov:
            diff.add(i)
    return diff


def col_label(i: int) -> str:
    return "Name" if i == 1 else f"field{i - 2}"


@dataclass
class ParamResult:
    param: str
    clean_add_a: list[int] = field(default_factory=list)
    clean_add_b: list[int] = field(default_factory=list)
    edit_only_a: list[int] = field(default_factory=list)   # take A
    edit_only_b: list[int] = field(default_factory=list)   # take B
    auto_merged: list[dict] = field(default_factory=list)  # disjoint field edits
    field_conflicts: list[dict] = field(default_factory=list)
    add_collisions: list[dict] = field(default_factory=list)
    merged: Param = field(default_factory=dict)            # built when merging

    @property
    def conflict_count(self) -> int:
        return len(self.field_conflicts) + len(self.add_collisions)


def merge_param(name: str, v: Param, a: Param, b: Param, build: bool) -> ParamResult:
    r = ParamResult(name)
    # Base for a merged output: start from vanilla so untouched rows survive.
    if build:
        r.merged = {rid: list(cols) for rid, cols in v.items()}

    for rid in sorted(set(a) | set(b)):
        ra, rb, rv = a.get(rid), b.get(rid), v.get(rid)

        if ra is not None and rb is not None:
            if rv is None:
                # Both mods add the same new ID.
                if ra == rb:
                    if build:
                        r.merged[rid] = ra
                    continue
                r.add_collisions.append({
                    "id": rid,
                    "diff_cols": sorted(col_label(i) for i in changed_cols(ra, rb)),
                })
                continue
            # Both reference an existing vanilla row.
            da, db = changed_cols(rv, ra), changed_cols(rv, rb)
            if not da and not db:
                continue
            if da and not db:
                r.edit_only_a.append(rid)
                if build:
                    r.merged[rid] = ra
                continue
            if db and not da:
                r.edit_only_b.append(rid)
                if build:
                    r.merged[rid] = rb
                continue
            # Both changed something. Conflict only where they overlap AND differ.
            overlap = {i for i in (da & db) if (ra[i] if i < len(ra) else "") !=
                       (rb[i] if i < len(rb) else "")}
            if overlap:
                r.field_conflicts.append({
                    "id": rid,
                    "cols": sorted(col_label(i) for i in overlap),
                })
                continue
            # Disjoint (or agreeing) edits -> combine onto the vanilla base.
            merged_row = list(rv)
            while len(merged_row) < max(len(ra), len(rb)):
                merged_row.append("")
            for i in da:
                merged_row[i] = ra[i] if i < len(ra) else ""
            for i in db:
                merged_row[i] = rb[i] if i < len(rb) else ""
            r.auto_merged.append({
                "id": rid,
                "from_a": sorted(col_label(i) for i in da),
                "from_b": sorted(col_label(i) for i in db),
            })
            if build:
                r.merged[rid] = merged_row

        elif ra is not None:        # only A has the row
            if rv is None:
                r.clean_add_a.append(rid)
                if build:
                    r.merged[rid] = ra
            elif changed_cols(rv, ra):
                r.edit_only_a.append(rid)
                if build:
                    r.merged[rid] = ra
        else:                       # only B has the row
            if rv is None:
                r.clean_add_b.append(rid)
                if build:
                    r.merged[rid] = rb
            elif changed_cols(rv, rb):
                r.edit_only_b.append(rid)
                if build:
                    r.merged[rid] = rb
    return r


def write_param(path: Path, p: Param) -> None:
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    for rid in sorted(p):
        w.writerow(p[rid])
    path.write_text(buf.getvalue(), encoding="utf-8")


def print_result(r: ParamResult) -> None:
    print(f"\n### {r.param}")
    print(f"  clean additions : A={len(r.clean_add_a)}  B={len(r.clean_add_b)}")
    print(f"  single-mod edits: A={len(r.edit_only_a)}  B={len(r.edit_only_b)}")
    print(f"  auto-merged rows: {len(r.auto_merged)} (disjoint field edits)")
    if r.add_collisions:
        print(f"  ADD COLLISIONS ({len(r.add_collisions)}) — both mods add same new ID:")
        for c in r.add_collisions:
            print(f"      id {c['id']}: differ on {', '.join(c['diff_cols'])}")
    if r.field_conflicts:
        print(f"  FIELD CONFLICTS ({len(r.field_conflicts)}) — both edit same field:")
        for c in r.field_conflicts:
            print(f"      id {c['id']}: {', '.join(c['cols'])}")
    if not r.conflict_count:
        print("  -> no conflicts; fully auto-mergeable.")


def resolve_pair(name: str, vp: Path | None, ap: Path, bp: Path,
                 out: Path | None) -> ParamResult:
    v = load_param(vp) if vp and vp.exists() else {}
    res = merge_param(name, v, load_param(ap), load_param(bp), build=out is not None)
    if out is not None:
        if res.conflict_count:
            # Leave conflicting rows at their vanilla value rather than guess.
            print(f"  (merged CSV written; {res.conflict_count} conflicting "
                  f"row(s) kept at vanilla — resolve in Smithbox)")
        write_param(out, res.merged)
    return res


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--vanilla", type=Path, help="Vanilla CSV or dir (base)")
    ap.add_argument("--a", required=True, type=Path, help="Mod A CSV or dir")
    ap.add_argument("--b", required=True, type=Path, help="Mod B CSV or dir")
    ap.add_argument("--out", type=Path, help="Merged CSV out (single-param mode)")
    ap.add_argument("--out-dir", type=Path, help="Merged CSV dir (directory mode)")
    ap.add_argument("--json", type=Path, help="Write full JSON report")
    args = ap.parse_args(argv)

    results: list[ParamResult] = []
    if args.a.is_dir():
        if not args.b.is_dir():
            ap.error("--a is a dir but --b is not")
        if args.out_dir:
            args.out_dir.mkdir(parents=True, exist_ok=True)
        names = sorted({p.name for p in args.a.glob("*.csv")} &
                       {p.name for p in args.b.glob("*.csv")})
        if not names:
            ap.error("no matching *.csv filenames between --a and --b dirs")
        for nm in names:
            vp = (args.vanilla / nm) if args.vanilla else None
            out = (args.out_dir / nm) if args.out_dir else None
            results.append(resolve_pair(nm, vp, args.a / nm, args.b / nm, out))
    else:
        name = args.a.stem
        results.append(resolve_pair(name, args.vanilla, args.a, args.b, args.out))

    total_conflicts = sum(r.conflict_count for r in results)
    print(f"\n{'='*56}")
    print(f"Params analyzed: {len(results)}   Total conflicts: {total_conflicts}")
    for r in results:
        print_result(r)

    if args.json:
        payload = [{k: v for k, v in r.__dict__.items() if k != "merged"}
                   for r in results]
        args.json.write_text(json.dumps(payload, indent=2))
        print(f"\nJSON written to {args.json}")
    return 1 if total_conflicts else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
