#!/usr/bin/env python3
"""Refactor safety net: are two builds the same fonts, table for table?

A refactor must not move a single glyph (CLAUDE.md). This compares every
table's raw bytes between two directories of fonts with the same file names.
`head` is compared without its timestamps and checksum, which change on
every build.

    python tools/identical.py <before-dir> <after-dir>

Exits 1 and names each differing font and table.
"""

import sys
from pathlib import Path

from fontTools.ttLib import TTFont

# head fields that change on every save, whatever the code does.
VOLATILE_HEAD_FIELDS = ("created", "modified", "checkSumAdjustment")


def head_without_timestamps(font: TTFont) -> dict[str, object]:
    """The head table as a dict, minus the fields every build changes.

    >>> head_without_timestamps(TTFont("a.otf"))["unitsPerEm"]
    2000
    """
    head = vars(font["head"]).copy()
    for field in VOLATILE_HEAD_FIELDS:
        head.pop(field, None)
    return head


def differing_tables(before: Path, after: Path) -> list[str]:
    """Tags of the tables whose bytes differ, plus any table only one font has.

    >>> differing_tables(Path("old/a.otf"), Path("new/a.otf"))
    []
    """
    old, new = TTFont(before), TTFont(after)
    tags = sorted(set(old.reader.keys()) | set(new.reader.keys()))
    head = (
        [] if head_without_timestamps(old) == head_without_timestamps(new) else ["head"]
    )
    return head + [t for t in tags if t != "head" and _bytes_differ(old, new, t)]


def _bytes_differ(old: TTFont, new: TTFont, tag: str) -> bool:
    if tag not in old.reader or tag not in new.reader:
        return True
    return old.reader[tag] != new.reader[tag]


def compare_dirs(before: Path, after: Path) -> list[str]:
    """One line per font that differs; empty when the builds are identical."""
    names = sorted(p.name for p in before.glob("*.otf"))
    if not names:
        raise SystemExit(f"no .otf files in {before} (expected a build directory)")
    problems = []
    for name in names:
        if not (after / name).exists():
            problems.append(f"{name}: missing from {after}")
            continue
        tables = differing_tables(before / name, after / name)
        if tables:
            problems.append(f"{name}: {' '.join(tables)}")
    return problems


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        raise SystemExit(f"usage: identical.py <before-dir> <after-dir> (got {argv})")
    problems = compare_dirs(Path(argv[0]), Path(argv[1]))
    for line in problems:
        print(line)
    print("identical" if not problems else f"{len(problems)} font(s) differ")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
