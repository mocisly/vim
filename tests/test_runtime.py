#!/usr/bin/env python3
"""Run the Windows same-DLL acceptance suite against an existing build."""

import argparse
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent.parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--configuration", choices=("Debug", "Release"), default="Debug")
    parser.add_argument("--fresh-cycles", type=int, default=5)
    args = parser.parse_args()
    directory = ROOT / "build/vs2026-qt" / args.configuration / "vim"
    dll = directory / "vimcore.dll"
    host = directory / "vim_qt_host.exe"
    if not dll.is_file() or not host.is_file():
        parser.error(f"Build vim_qt_host and vim for {args.configuration} first")
    if args.fresh_cycles < 1:
        parser.error("--fresh-cycles must be positive")

    env = os.environ.copy()
    env.pop("PYTHONOPTIMIZE", None)
    env["VIMRUNTIME"] = str(directory / "runtime")
    env["PATH"] = sys.base_prefix + os.pathsep + env.get("PATH", "")
    startup = subprocess.STARTUPINFO()
    startup.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    startup.wShowWindow = subprocess.SW_HIDE

    def run(label, command, timeout=120):
        with subprocess.Popen(command, cwd=ROOT, env=env, startupinfo=startup,
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                              text=True, errors="replace") as process:
            try:
                stdout, stderr = process.communicate(timeout=timeout)
            except subprocess.TimeoutExpired:
                # The console driver creates a child with its own console.
                # Stop only this known test process and its descendants.
                if process.poll() is None:
                    subprocess.run(["taskkill", "/PID", str(process.pid), "/T", "/F"],
                                   capture_output=True, startupinfo=startup, timeout=10)
                if process.poll() is None:
                    process.kill()
                process.communicate(timeout=10)
                raise RuntimeError(f"{label} timed out") from None
        if process.returncode:
            print(stdout, end="")
            print(stderr, end="", file=sys.stderr)
            if command[0] == str(host):
                log = directory / "vim-qt-host-selftest.log"
                if log.exists():
                    print(log.read_text(encoding="utf-8", errors="replace"))
            raise RuntimeError(f"{label} failed with exit code {process.returncode}")
        print(f"PASS {args.configuration}: {label}", flush=True)

    for script, extra in (
        ("test_two_instances.py", ["--async", "--terminal", "--compare-standalone",
                                   "--fresh-cycles", str(args.fresh_cycles)]),
        ("test_gui_instances.py", []),
        ("test_gui_input.py", []),
        ("test_console_instances.py", ["--fatal", "--fresh-cycles", str(args.fresh_cycles)]),
    ):
        run(script, [sys.executable, str(ROOT / "tests" / script), "--dll", str(dll), *extra])

    # These probes use fixed files beside the host and must run sequentially.
    modes = ["--self-test", "--self-test-close-retry", "--self-test-python"]
    modes += ["--self-test-python-quit=" + mode
              for mode in ("command", "function", "eval", "bindeval", "option", "pydo")]
    for mode in modes:
        run(mode, [str(host), mode], timeout=20)


if __name__ == "__main__":
    main()
