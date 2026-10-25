#!/usr/bin/env python3
"""Smoke test two native GUI Vim windows from one vimcore.dll process."""

import ctypes
import argparse
import os
from pathlib import Path
import tempfile


ROOT = Path(__file__).resolve().parent.parent
DLL = ROOT / "build/vs2026-qt/Debug/vim/vimcore.dll"


def quoted(path: Path) -> str:
    return "'" + path.as_posix().replace("'", "''") + "'"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dll", type=Path, default=DLL)
    dll = parser.parse_args().dll.resolve()
    with tempfile.TemporaryDirectory(prefix="vim-gui-instances-", dir=ROOT / "build/vs2026-qt", ignore_cleanup_errors=True) as directory_name:
        directory = Path(directory_name)
        with os.add_dll_directory(str(dll.parent)):
            core = ctypes.CDLL(str(dll))
            core.vim_runtime_instance_create.argtypes = [ctypes.c_int, ctypes.POINTER(ctypes.c_char_p)]
            core.vim_runtime_instance_create.restype = ctypes.c_void_p
            core.vim_runtime_instance_wait.argtypes = [ctypes.c_void_p, ctypes.c_ulong, ctypes.POINTER(ctypes.c_int)]
            core.vim_runtime_instance_wait.restype = ctypes.c_int
            core.vim_runtime_instance_destroy.argtypes = [ctypes.c_void_p]
            core.vim_runtime_instance_destroy.restype = ctypes.c_int
            instances = []
            try:
                for name in ("A", "B"):
                    script = directory / f"{name}.vim"
                    result = directory / f"{name}.result"
                    script.write_text(
                        f"let g:instance_marker = '{name}'\n"
                        "split\n"
                        f"call timer_start(250, {{-> writefile([g:instance_marker, string(winnr('$'))], {quoted(result)})}})\n"
                        "call timer_start(1200, {-> execute('qa!')})\n",
                        encoding="utf-8",
                    )
                    argv = [b"vim", b"-g", b"-f", b"-N", b"-u", b"NONE", b"-i", b"NONE", b"-S", str(script).encode("utf-8")]
                    arguments = (ctypes.c_char_p * len(argv))(*argv)
                    instance = core.vim_runtime_instance_create(len(argv), arguments)
                    if not instance:
                        raise RuntimeError(f"create failed: {name}")
                    instances.append(instance)
                for instance in instances:
                    status = ctypes.c_int(-999)
                    if core.vim_runtime_instance_wait(instance, 10000, ctypes.byref(status)) != 1:
                        print("GUI probe files:", sorted(path.name for path in directory.glob("*")), flush=True)
                        if os.environ.get("VIM_RUNTIME_DEBUGBREAK"):
                            ctypes.WinDLL("kernel32").DebugBreak()
                        raise RuntimeError("GUI instance did not exit")
                    if status.value != 0:
                        raise RuntimeError(f"GUI instance exited with {status.value}")
            finally:
                unfinished = []
                for instance in instances:
                    if core.vim_runtime_instance_destroy(instance) != 1:
                        unfinished.append(instance)
                if unfinished:
                    raise RuntimeError("GUI workers are still running after the exit deadline")
            for name in ("A", "B"):
                result = directory / f"{name}.result"
                if not result.exists() or result.read_text(encoding="utf-8").splitlines() != [name, "2"]:
                    raise AssertionError(f"GUI callback failed for {name}")
        print("Two GUI Vim instances ran concurrent timers and exited independently.")


if __name__ == "__main__":
    main()
