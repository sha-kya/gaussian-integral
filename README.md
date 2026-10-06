# Gaussian integral, animated

An 88-second [Manim Community Edition](https://www.manim.community/) animation of
the classic proof that

    ∫_{-∞}^{∞} e^{-x²} dx = √π

![preview of the full animation](docs/preview.gif)

The algebra on the left morphs from one line to the next with
`TransformMatchingTex`, while the geometry on the right follows along: the bell
curve and its growing area, the 3D surface `z = e^{-(x²+y²)}`, a square grid
bending into polar rings, the area element `r dr dθ`, the polar disc unrolling
into a rectangle, and the area under `r e^{-r²}` filling up to ½.

## Quick start

```bash
git clone <this repo> && cd gaussian-integral
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

manim -pql main.py FullProof            # 480p15 preview, opens the video
manim -qh --fps 60 main.py FullProof    # final 1080p60
```

Output goes to `media/videos/main/<quality>/FullProof.mp4`. Developed and tested
on Python 3.13 with Manim 0.21.

### System dependencies

Manim needs Cairo and Pango, ffmpeg, and a LaTeX install that includes `dvisvgm`.

**Ubuntu / Debian** (this is the set the project was tested with)

```bash
sudo apt install build-essential python3-dev pkg-config libcairo2-dev libpango1.0-dev \
    ffmpeg texlive-latex-extra texlive-fonts-recommended texlive-science dvisvgm
```

**macOS** (follows Manim's install docs; not tested here)

```bash
brew install cairo pango pkg-config ffmpeg
brew install --cask mactex-no-gui      # or basictex, then tlmgr install dvisvgm standalone preview
```

The text uses the font named in `tokens.json` (default Inter). If it is not
installed, `theme.py` falls back to Helvetica Neue, Arial or DejaVu Sans.

## Rendering one step

Each step is its own scene. Earlier steps are replayed silently so the scene
starts in the right state, and only the chosen step is rendered.

```bash
manim -pql main.py Step4
python scripts/render.py --step 4                 # same thing
python scripts/render.py --step all -q h --fps 60
python scripts/render.py --step 3 --theme my_tokens.json
```

| Scene | What it shows | Length |
|-------|---------------|--------|
| `Step1` | Title card, `I = ∫ e^{-x²} dx`, the area sweeping out to ±∞ | 14 s |
| `Step2` | Square it: a second copy appears with variable `y` | 6 s |
| `Step3` | Merge into `∬ e^{-(x²+y²)}`; the 3D surface tilts up and spins | 12 s |
| `Step4` | Cartesian grid becomes polar; `dx dy → r dr dθ` and the Jacobian wedge | 16 s |
| `Step5` | The polar disc unrolls into a θ–r rectangle; the integral splits | 9 s |
| `Step6` | `∫dθ = 2π`; `u = r²` turns the radial integral into ½ | 18 s |
| `Step7` | `I² = π`, `√(I²) = √π`, `I = √π`, and the bell labelled `√π` | 17 s |

`FullProof` plays all seven back to back.

## Repository layout

| Path | Purpose |
|------|---------|
| `main.py` | The scenes: `ProofScene` holds the helpers and `step_1` … `step_7`. |
| `math_steps.py` | Every LaTeX string and caption. |
| `theme.py` | Loads colours, font and sizes from `tokens.json`. |
| `tokens.json` | Default design tokens, shaped like a Figma variables export. |
| `scripts/render.py` | Render a step without remembering scene names. |
| `scripts/figma_tokens.py` | Pull tokens from a Figma file into `tokens.json`. |
| `assets/` | Optional Figma-exported SVGs (see below). |
| `tests/` | Unit tests, plus renders of two scenes when LaTeX is installed. |
| `.github/workflows/ci.yml` | Runs ruff and the unit tests on every push and pull request. |

To change what an equation says, edit `math_steps.py`. Parts with an identical
string in two neighbouring equations are morphed into each other, so keep those
strings the same when editing.

## Design tokens and Figma

Python cannot drive Figma's UI, so Figma is the source of truth for the look
and Manim does the animating.

1. Define variables in Figma. Collections and names follow `tokens.json`:
   `color/{background,text,muted,integrand,result,geometry,grid,surface-low,surface-high}`,
   `font/{family,title-size,caption-size}`, `radius/box`, `spacing/gutter`.
2. Get them into `tokens.json` by one of:
   - `FIGMA_TOKEN=... FIGMA_FILE_KEY=... python scripts/figma_tokens.py`. The token
     needs the `file_variables:read` scope, and Figma limits the variables REST
     API to Enterprise plans.
   - A variables export plugin, or editing `tokens.json` by hand.
3. Render as usual. To use another file, set `GAUSSIAN_THEME=path/to/tokens.json`
   or pass `--theme` to `scripts/render.py`.

A missing `tokens.json`, or keys missing from it, fall back to the defaults in
`theme.py`. A file that is not valid JSON raises.

**SVG assets.** Export a logo from Figma as `assets/title_card.svg` and it is
shown above the title on the opening card. Without it the card renders without a
logo.

## Development

```bash
pip install -r requirements-dev.txt
ruff check .
pytest
```

`tests/test_render.py` renders `Step2` and `Step5` and is skipped when `latex`,
`dvisvgm` or `ffmpeg` are missing, which is the case on the CI runner. CI
therefore covers lint and the unit tests only.

## Implementation notes

- The 3D step runs in a `ThreeDScene`. While the camera is tilted the text is
  pinned to the screen, and the surface is spun about its own axis. Because the
  bell is rotationally symmetric, that looks the same as an orbiting camera.
- `MorphTex` in `main.py` wraps `TransformMatchingTex`. Manim's own `key_map`
  fails when the two parts have different glyph counts (`I` → `I²`), so mapped
  parts here are paired with a plain `Transform`.
- A part that appears once in one equation and twice in the next cannot be
  paired by `TransformMatchingTex`. `math_steps.disambiguate` appends an
  invisible `\relax` to repeats so they stay one-to-one.
- `scripts/figma_tokens.py` was checked against a hand-written sample of the
  REST response, not a live Figma file.

## License

MIT, see [LICENSE](LICENSE).
