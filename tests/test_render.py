import shutil
import subprocess
import sys
from pathlib import Path

import pytest
from render import build_command, parse_args

ROOT = Path(__file__).resolve().parent.parent
HAS_TOOLCHAIN = all(shutil.which(tool) for tool in ("latex", "dvisvgm", "ffmpeg"))


def test_render_script_shows_help():
    done = subprocess.run([sys.executable, str(ROOT / "scripts" / "render.py"), "--help"], capture_output=True)
    assert done.returncode == 0


def test_render_command_for_one_step():
    args = parse_args(["--step", "4", "-q", "h", "--fps", "60", "--no-preview"])
    command = build_command(args)
    assert command[:4] == [sys.executable, "-m", "manim", "-qh"]
    assert command[-3:] == ["60", str(ROOT / "main.py"), "Step4"]
    assert "-p" not in command


def test_full_proof_previews_by_default():
    command = build_command(parse_args([]))
    assert "-p" in command
    assert command[-1] == "FullProof"


@pytest.mark.skipif(not HAS_TOOLCHAIN, reason="needs LaTeX, dvisvgm and ffmpeg")
@pytest.mark.parametrize("scene", ["Step2", "Step5"])
def test_scene_renders(scene, tmp_path):
    command = [sys.executable, "-m", "manim", "-ql", "--disable_caching", "--media_dir", str(tmp_path)]
    command += ["main.py", scene]
    subprocess.run(command, cwd=ROOT, check=True, capture_output=True)
    assert (tmp_path / "videos" / "main" / "480p15" / f"{scene}.mp4").is_file()
