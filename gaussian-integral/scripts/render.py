"""Render one step or the whole proof: python scripts/render.py --step 4 [-q h] [--fps 60]"""

import argparse
import os
import subprocess
import sys
from pathlib import Path

here = Path(__file__).resolve().parent.parent

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--step", default="all", choices=[*"1234567", "all"])
parser.add_argument("-q", "--quality", default="l", choices=list("lmhpk"))
parser.add_argument("--fps", type=int)
parser.add_argument("--theme", help="tokens.json to use instead of the default")
parser.add_argument("--no-preview", action="store_true")
args = parser.parse_args()

scene = "FullProof" if args.step == "all" else f"Step{args.step}"
command = [sys.executable, "-m", "manim", f"-q{args.quality}"]
if not args.no_preview:
    command.append("-p")
if args.fps:
    command += ["--fps", str(args.fps)]
command += [str(here / "main.py"), scene]

env = dict(os.environ)
if args.theme:
    env["GAUSSIAN_THEME"] = str(Path(args.theme).resolve())
print("$", " ".join(command))
sys.exit(subprocess.call(command, cwd=here, env=env))
