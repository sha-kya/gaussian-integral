import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
HAS_TOOLCHAIN = all(shutil.which(tool) for tool in ("latex", "dvisvgm", "ffmpeg"))


def test_render_script_shows_help():
    done = subprocess.run([sys.executable, str(ROOT / "scripts" / "render.py"), "--help"], capture_output=True)
    assert done.returncode == 0


@pytest.mark.skipif(not HAS_TOOLCHAIN, reason="needs LaTeX, dvisvgm and ffmpeg")
@pytest.mark.parametrize("scene", ["Step2", "Step5"])
def test_scene_renders(scene, tmp_path):
    command = [sys.executable, "-m", "manim", "-ql", "--disable_caching", "--media_dir", str(tmp_path)]
    command += ["main.py", scene]
    subprocess.run(command, cwd=ROOT, check=True, capture_output=True)
    assert (tmp_path / "videos" / "main" / "480p15" / f"{scene}.mp4").is_file()
