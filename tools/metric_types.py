"""Results shared by font measurement and its Markdown reports."""

from typing import NotRequired, TypedDict

Spacing = TypedDict(
    "Spacing",
    {
        "mean_gap_px@40": float,
        "cv": float,
        "tightest": list[str],
        "loosest": list[str],
        "n": int,
    },
)


class VisualAngle(TypedDict):
    x_height_mm: float
    degrees: float


class RomanItalic(TypedDict):
    mean: float
    per_letter: dict[str, float]


class FontMetrics(TypedDict):
    font: str
    x_height_em: float
    confusability: dict[int | str, dict[str, float]]
    spacing: Spacing
    visual_angle: dict[str, VisualAngle]
    sharpness: dict[str, float]
    roman_italic: NotRequired[RomanItalic]
