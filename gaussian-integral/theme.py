"""Colours, font and sizes for the video, read from tokens.json.

The file mirrors a Figma variables export: {"color": {"integrand": "#58C4DD"},
"font": {"family": "Inter"}, ...}. Set GAUSSIAN_THEME to use another file.
A missing file or missing keys fall back to the defaults below; a malformed
file raises.
"""

import json
import os
from dataclasses import dataclass, replace
from pathlib import Path

import manimpango
from manim import SVGMobject

HERE = Path(__file__).resolve().parent
FALLBACK_FONTS = ("Inter", "Helvetica Neue", "Helvetica", "Arial", "DejaVu Sans", "Liberation Sans")


@dataclass(frozen=True)
class Theme:
    background: str = "#0F1115"
    text: str = "#E8EAF0"
    muted: str = "#8B92A5"
    integrand: str = "#58C4DD"
    result: str = "#FFC857"
    geometry: str = "#7C8CF8"
    grid: str = "#2A2F3A"
    surface_low: str = "#2B3A8C"
    surface_high: str = "#58C4DD"
    font_family: str = "Inter"
    title_size: float = 34.0
    caption_size: float = 30.0
    box_radius: float = 0.12
    gutter: float = 0.5


# Theme field -> (collection, variable name) in tokens.json
TOKEN_NAMES = {
    "background": ("color", "background"),
    "text": ("color", "text"),
    "muted": ("color", "muted"),
    "integrand": ("color", "integrand"),
    "result": ("color", "result"),
    "geometry": ("color", "geometry"),
    "grid": ("color", "grid"),
    "surface_low": ("color", "surface-low"),
    "surface_high": ("color", "surface-high"),
    "font_family": ("font", "family"),
    "title_size": ("font", "title-size"),
    "caption_size": ("font", "caption-size"),
    "box_radius": ("radius", "box"),
    "gutter": ("spacing", "gutter"),
}


def load_theme(path=None):
    path = Path(path or os.environ.get("GAUSSIAN_THEME") or HERE / "tokens.json")
    tokens = json.loads(path.read_text()) if path.is_file() else {}

    defaults = Theme()
    chosen = {}
    for field, (collection, name) in TOKEN_NAMES.items():
        if name in tokens.get(collection, {}):
            chosen[field] = type(getattr(defaults, field))(tokens[collection][name])
    theme = replace(defaults, **chosen)

    installed = set(manimpango.list_fonts())
    family = next((f for f in (theme.font_family, *FALLBACK_FONTS) if f in installed), theme.font_family)
    return replace(theme, font_family=family)


def load_logo():
    """assets/title_card.svg as a mobject, or None when the file is absent."""
    path = HERE / "assets" / "title_card.svg"
    return SVGMobject(str(path)) if path.is_file() else None
