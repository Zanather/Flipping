#!/usr/bin/env python3
"""
conflict_scan.py — Conflict detection for FromSoftware mod merges.

Compares two WitchyBND-unpacked mod trees (e.g. two c0000.anibnd folders) and
reports where they collide, so you know exactly what needs hand-merging before
you repack. Optionally takes the vanilla-unpacked tree as a 3-way base so that
files a mod left untouched are not reported as conflicts.

Designed for the WitchyBND workflow:
    1. WitchyBND unpacks  c0000.anibnd.dcx  ->  c0000-anibnd/  (hkx, tae, xml)
    2. Run this on mod A's folder vs mod B's folder (plus optional vanilla)
    3. Hand-merge only what it flags; everything else is auto-mergeable

Pure stdlib. No dependencies. Usage:
    python conflict_scan.py --a MOD_A_DIR --b MOD_B_DIR [--vanilla VANILLA_DIR]
                            [--json report.json]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path

# Player/character animation clips: a00_003000.hkx, a000_003000.hkx, etc.
ANIM_RE = re.compile(r"^a\d+_\d+\.hkx$", re.IGNORECASE)
# TimeActEvent files (WitchyBND unpacks these to .tae.xml; raw is .tae)
TAE_RE = re.compile(r"\.tae(\.xml)?$", re.IGNORECASE)


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def _localname(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _subtree_hash(el: ET.Element) -> str:
    """Whitespace-normalized hash of an element's full subtree."""
    raw = ET.tostring(el, encoding="unicode")
    norm = re.sub(r">\s+<", "><", raw.strip())
    return hashlib.sha256(norm.encode("utf-8")).hexdigest()


def parse_tae_animations(path: Path) -> dict[str, str] | None:
    """
    Map each animation in a WitchyBND .tae.xml to a hash of its subtree.

    Tag-tolerant: finds elements whose local name ends in "Animation" (but not
    the "Animations" container) and reads the animation ID from an attribute or
    a child ID element. Returns None if the file can't be parsed as TAE XML so
    callers can fall back to file-level comparison.
    """
    try:
        root = ET.parse(path).getroot()
    except ET.ParseError:
        return None
    anims: dict[str, str] = {}
    for el in root.iter():
        name = _localname(el.tag).lower()
        if not name.endswith("animation") or name == "animations":
            continue
        aid = None
        for key in ("ID", "id", "Id", "AnimationID", "animID"):
            if key in el.attrib:
                aid = el.attrib[key]
                break
        if aid is None:
            for child in el:
                if _localname(child.tag).lower() in ("id", "animationid", "animid"):
                    aid = (child.text or "").strip()
                    break
        if aid:
            anims[aid] = _subtree_hash(el)
    return anims or None


def index_tree(root: Path) -> dict[str, str]:
    """Map every file to its hash, keyed by path relative to root (posix)."""
    out: dict[str, str] = {}
    for p in sorted(root.rglob("*")):
        if p.is_file():
            out[p.relative_to(root).as_posix()] = sha(p)
    return out


@dataclass
class Report:
    a_root: str
    b_root: str
    vanilla_root: str | None
    # Same relative path in both mods, differing content.
    overwrite_conflicts: list[dict] = field(default_factory=list)
    # Animation-ID collisions (aXXX_YYYYYY.hkx in both, differing content).
    anim_id_collisions: list[str] = field(default_factory=list)
    # TAE files touched by both mods.
    tae_conflicts: list[str] = field(default_factory=list)
    # Per-animation breakdown of each conflicting .tae.xml (needs vanilla base).
    tae_detail: list[dict] = field(default_factory=list)
    # Files only one mod added relative to vanilla — these merge cleanly.
    clean_additions_a: list[str] = field(default_factory=list)
    clean_additions_b: list[str] = field(default_factory=list)
    # Both edited the path but only one differs from vanilla -> auto-resolvable.
    auto_resolvable: list[dict] = field(default_factory=list)

    def to_json(self) -> str:
        return json.dumps(self.__dict__, indent=2)


def kind(rel: str) -> str:
    name = rel.rsplit("/", 1)[-1]
    if ANIM_RE.match(name):
        return "anim"
    if TAE_RE.search(name):
        return "tae"
    return "other"


def analyze_tae(a_file: Path, b_file: Path, v_file: Path, rel: str) -> dict | None:
    """Per-animation breakdown of a conflicting .tae.xml using vanilla as base."""
    va = parse_tae_animations(v_file)
    aa = parse_tae_animations(a_file)
    bb = parse_tae_animations(b_file)
    if va is None or aa is None or bb is None:
        return None

    def changed(side: dict[str, str]) -> set[str]:
        ids = set(va) | set(side)
        return {i for i in ids if va.get(i) != side.get(i)}

    a_ch, b_ch = changed(aa), changed(bb)
    overlap = {i for i in (a_ch & b_ch) if aa.get(i) != bb.get(i)}
    return {
        "file": rel,
        "a_changed": sorted(a_ch),
        "b_changed": sorted(b_ch),
        "conflict_animations": sorted(overlap),
        "a_only": sorted(a_ch - overlap),
        "b_only": sorted(b_ch - overlap),
        # If both edited the file but never the same animation, it's mergeable
        # at animation granularity (copy each side's animations together).
        "mergeable": not overlap,
    }


def scan(a: Path, b: Path, vanilla: Path | None) -> Report:
    ia, ib = index_tree(a), index_tree(b)
    iv = index_tree(vanilla) if vanilla else {}
    rep = Report(str(a), str(b), str(vanilla) if vanilla else None)

    shared = sorted(set(ia) & set(ib))
    for rel in shared:
        if ia[rel] == ib[rel]:
            continue  # identical in both mods -> no conflict
        k = kind(rel)
        if vanilla and rel in iv:
            a_changed = ia[rel] != iv[rel]
            b_changed = ib[rel] != iv[rel]
            if a_changed and not b_changed:
                rep.auto_resolvable.append({"file": rel, "take": "A"})
                continue
            if b_changed and not a_changed:
                rep.auto_resolvable.append({"file": rel, "take": "B"})
                continue
        # True conflict: both changed it (or no vanilla base to decide).
        rep.overwrite_conflicts.append({"file": rel, "kind": k})
        if k == "anim":
            rep.anim_id_collisions.append(rel)
        elif k == "tae":
            rep.tae_conflicts.append(rel)
            if vanilla and rel in iv and rel.lower().endswith(".xml"):
                detail = analyze_tae(a / rel, b / rel, vanilla / rel, rel)
                if detail:
                    rep.tae_detail.append(detail)

    if vanilla:
        for rel in sorted(set(ia) - set(iv)):
            if rel not in ib:
                rep.clean_additions_a.append(rel)
        for rel in sorted(set(ib) - set(iv)):
            if rel not in ia:
                rep.clean_additions_b.append(rel)
    return rep


def print_report(rep: Report) -> None:
    def header(title: str, n: int) -> None:
        print(f"\n=== {title} ({n}) ===")

    print(f"Mod A : {rep.a_root}")
    print(f"Mod B : {rep.b_root}")
    print(f"Base  : {rep.vanilla_root or '(none — every shared diff is a conflict)'}")

    header("OVERWRITE CONFLICTS — hand-merge required", len(rep.overwrite_conflicts))
    for c in rep.overwrite_conflicts:
        print(f"  [{c['kind']:5}] {c['file']}")

    header("ANIMATION ID COLLISIONS — re-ID one side + fix references", len(rep.anim_id_collisions))
    for f in rep.anim_id_collisions:
        print(f"  {f}")

    header("TAE CONFLICTS — diff/merge the .tae.xml", len(rep.tae_conflicts))
    for f in rep.tae_conflicts:
        print(f"  {f}")

    if rep.tae_detail:
        header("TAE PER-ANIMATION DETAIL", len(rep.tae_detail))
        for d in rep.tae_detail:
            print(f"  {d['file']}")
            if d["conflict_animations"]:
                print(f"      CONFLICT animations (both edited): "
                      f"{', '.join(d['conflict_animations'])}")
            if d["a_only"]:
                print(f"      A-only animations (mergeable): {', '.join(d['a_only'])}")
            if d["b_only"]:
                print(f"      B-only animations (mergeable): {', '.join(d['b_only'])}")
            if d["mergeable"]:
                print("      -> mergeable: mods edit DIFFERENT animations; "
                      "combine both sets, no per-animation conflict.")

    header("AUTO-RESOLVABLE — only one mod changed vs vanilla", len(rep.auto_resolvable))
    for c in rep.auto_resolvable:
        print(f"  take {c['take']}: {c['file']}")

    header("CLEAN ADDITIONS (A)", len(rep.clean_additions_a))
    for f in rep.clean_additions_a:
        print(f"  + {f}")
    header("CLEAN ADDITIONS (B)", len(rep.clean_additions_b))
    for f in rep.clean_additions_b:
        print(f"  + {f}")

    conflicts = len(rep.overwrite_conflicts)
    print(f"\n{'-'*52}")
    print(f"RESULT: {conflicts} conflict(s) need attention, "
          f"{len(rep.auto_resolvable)} auto-resolvable.")


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--a", required=True, type=Path, help="Mod A unpacked dir")
    ap.add_argument("--b", required=True, type=Path, help="Mod B unpacked dir")
    ap.add_argument("--vanilla", type=Path, help="Vanilla unpacked dir (3-way base)")
    ap.add_argument("--json", type=Path, help="Write JSON report to this path")
    args = ap.parse_args(argv)

    for label, d in (("--a", args.a), ("--b", args.b)):
        if not d.is_dir():
            ap.error(f"{label} is not a directory: {d}")
    if args.vanilla and not args.vanilla.is_dir():
        ap.error(f"--vanilla is not a directory: {args.vanilla}")

    rep = scan(args.a, args.b, args.vanilla)
    print_report(rep)
    if args.json:
        args.json.write_text(rep.to_json())
        print(f"\nJSON written to {args.json}")
    # Exit non-zero when real conflicts exist (handy for CI/skills).
    return 1 if rep.overwrite_conflicts else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
