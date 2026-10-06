import json

import pytest

from theme import Theme, load_theme


def write_tokens(tmp_path, tokens):
    path = tmp_path / "tokens.json"
    path.write_text(json.dumps(tokens))
    return path


def test_missing_file_gives_defaults(tmp_path):
    theme = load_theme(tmp_path / "nope.json")
    assert theme.integrand == Theme().integrand
    assert theme.gutter == Theme().gutter


def test_partial_tokens_override_only_what_they_name(tmp_path):
    path = write_tokens(
        tmp_path,
        {
            "color": {"result": "#00FF00", "surface-low": "#111111"},
            "font": {"title-size": 38.5},
            "radius": {"box": 0.3},
        },
    )
    theme = load_theme(path)
    assert (theme.result, theme.surface_low) == ("#00FF00", "#111111")
    assert (theme.title_size, theme.box_radius) == (38.5, 0.3)
    assert theme.integrand == Theme().integrand


def test_shipped_tokens_match_the_defaults():
    from pathlib import Path

    shipped = load_theme(Path(__file__).resolve().parent.parent / "tokens.json")
    defaults = Theme()
    for name in ("background", "text", "muted", "integrand", "result", "geometry", "grid"):
        assert getattr(shipped, name) == getattr(defaults, name)


def test_environment_variable_picks_the_file(tmp_path, monkeypatch):
    monkeypatch.setenv("GAUSSIAN_THEME", str(write_tokens(tmp_path, {"color": {"text": "#FFFFFF"}})))
    assert load_theme().text == "#FFFFFF"


def test_malformed_file_raises(tmp_path):
    path = tmp_path / "tokens.json"
    path.write_text("{nope")
    with pytest.raises(json.JSONDecodeError):
        load_theme(path)
