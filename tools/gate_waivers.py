"""Regressions accepted on purpose, each scoped to one version.

The gate (tools/check.py) fails when a confusable pair gets more than 0.01
worse. Some design changes trade one pair for another deliberately; the user
decides those, and each decision goes into gate_waivers.json: the version it
was made for, why, and for each family/pair/size the largest delta allowed.
A waiver applies only while tools/merge.py's VERSION is that version, so it
can never cover a later change by accident.
"""

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence, TypedDict, cast

HERE = Path(__file__).resolve().parent
WAIVERS_PATH = HERE / "gate_waivers.json"
MERGE_PATH = HERE / "merge.py"


class AllowedRegression(TypedDict):
    family: str
    pair: str
    px: str
    max_delta: float


class Decision(TypedDict):
    version: str
    decided: str
    reason: str
    allow: list[AllowedRegression]


@dataclass(frozen=True)
class Waiver:
    family: str
    pair: str
    px: str
    max_delta: float
    reason: str


def build_version(merge_py: Path = MERGE_PATH) -> str:
    """The VERSION line of merge.py; e.g. ``build_version()`` -> "1.0.0-beta.2"."""
    m = re.search(r'^VERSION = "([^"]+)"$', merge_py.read_text(), re.M)
    if not m:
        raise ValueError(f'no `VERSION = "x.y.z"` line in {merge_py}')
    return m.group(1)


def load_waivers(path: Path, version: str) -> list[Waiver]:
    """The waivers decided for `version`.

    >>> load_waivers(Path("tools/gate_waivers.json"), "1.0.0-beta.2")[0].pair
    't/1'
    """
    if not path.exists():
        return []
    loaded = json.loads(path.read_text())
    if not isinstance(loaded, list):
        raise ValueError(f"{path}: expected a list of decisions, got {loaded!r}")
    decisions = cast(list[Decision], loaded)
    return [
        _waiver(entry, decision)
        for decision in decisions
        if decision.get("version") == version
        for entry in decision["allow"]
    ]


def _waiver(entry: AllowedRegression, decision: Decision) -> Waiver:
    keys = {"family", "pair", "px", "max_delta"}
    if set(entry) != keys:
        raise ValueError(f"waiver {entry!r}: expected exactly the keys {sorted(keys)}")
    return Waiver(
        entry["family"],
        entry["pair"],
        str(entry["px"]),
        float(entry["max_delta"]),
        decision["reason"],
    )


def find_waiver(
    waivers: Sequence[Waiver], family: str, px: int | str, pair: str, delta: float
) -> Waiver | None:
    """The waiver that covers this regression, if one does."""
    for w in waivers:
        if (w.family, w.pair, w.px) == (family, pair, str(px)):
            return w if delta <= w.max_delta + 1e-9 else None
    return None
