"""Render one step or the whole proof."""

import argparse
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--step", default="all", choices=[*"1234567", "all"])
    parser.add_argument("-q", "--quality", default="l", choices=list("lmhpk"))
    parser.add_argument("--fps", type=int)
    parser.add_argument("--theme", help="tokens.json to use instead of the default")
    parser.add_argument("--no-preview", action="store_true")
    return parser.parse_args(argv)


def build_command(args):
    scene = "FullProof" if args.step == "all" else f"Step{args.step}"
    command = [sys.executable, "-m", "manim", f"-q{args.quality}"]
    if not args.no_preview:
        command.append("-p")
    if args.fps:
        command += ["--fps", str(args.fps)]
    return command + [str(HERE / "main.py"), scene]


def main(argv=None):
    args = parse_args(argv)
    command = build_command(args)
    env = dict(os.environ)
    if args.theme:
        env["GAUSSIAN_THEME"] = str(Path(args.theme).resolve())
    print("$", " ".join(command))
    return subprocess.call(command, cwd=HERE, env=env)


if __name__ == "__main__":
    sys.exit(main())
