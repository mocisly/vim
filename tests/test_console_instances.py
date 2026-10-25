#!/usr/bin/env python3
"""Exercise console-control delivery in an isolated, hidden Windows console.

The child loads vimcore.dll once. CtrlBreak is broadcast only to its new console,
never to the invoking terminal. --fatal also closes a separate child console and
requires both Vim instances to finish their own VimLeavePre hooks.
"""

from __future__ import annotations

import argparse
import ctypes
from ctypes import wintypes
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import traceback


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DLL = ROOT / "build/vs2026-qt/Debug/vim/vimcore.dll"


def quote(path: Path) -> str:
    return "'" + path.as_posix().replace("'", "''") + "'"


def wait_until(read, accept, description: str, timeout: float = 12):
    deadline = time.monotonic() + timeout
    last = None
    while time.monotonic() < deadline:
        try:
            last = read()
            if accept(last):
                return last
        except (OSError, ValueError):
            pass  # writefile() may still be replacing the observation.
        time.sleep(0.02)
    raise AssertionError(f"{description}: last observation {last!r}")


def kernel_functions():
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel.CreateFileW.argtypes = [wintypes.LPCWSTR, wintypes.DWORD,
                                  wintypes.DWORD, ctypes.c_void_p, wintypes.DWORD,
                                  wintypes.DWORD, wintypes.HANDLE]
    kernel.CreateFileW.restype = wintypes.HANDLE
    kernel.SetStdHandle.argtypes = [wintypes.DWORD, wintypes.HANDLE]
    kernel.SetStdHandle.restype = wintypes.BOOL
    kernel.GetConsoleMode.argtypes = [wintypes.HANDLE, ctypes.POINTER(wintypes.DWORD)]
    kernel.GetConsoleMode.restype = wintypes.BOOL
    kernel.GetConsoleWindow.restype = wintypes.HWND
    kernel.GenerateConsoleCtrlEvent.argtypes = [wintypes.DWORD, wintypes.DWORD]
    kernel.GenerateConsoleCtrlEvent.restype = wintypes.BOOL
    return kernel


def child(args) -> None:
    directory = args.directory
    kernel = kernel_functions()
    if not kernel.GetConsoleWindow():
        raise AssertionError("The probe child has no isolated console")

    # Keep Python's diagnostic stream in child.log while native Vim receives
    # real console handles instead of the redirected parent subprocess pipes.
    handles = []
    for name, identifiers in (("CONIN$", (-10,)), ("CONOUT$", (-11, -12))):
        handle = kernel.CreateFileW(name, 0xC0000000, 3, None, 3, 0, None)
        if handle == ctypes.c_void_p(-1).value:
            raise ctypes.WinError(ctypes.get_last_error())
        handles.append(handle)
        for identifier in identifiers:
            if not kernel.SetStdHandle(identifier & 0xFFFFFFFF, handle):
                raise ctypes.WinError(ctypes.get_last_error())

    def console_modes():
        values = []
        for handle in handles:
            value = wintypes.DWORD()
            if not kernel.GetConsoleMode(handle, ctypes.byref(value)):
                raise ctypes.WinError(ctypes.get_last_error())
            values.append(value.value)
        return values

    original_modes = console_modes()
    instances = {}
    with os.add_dll_directory(str(args.dll.parent)):
        core = ctypes.CDLL(str(args.dll))
        core.vim_runtime_instance_create.argtypes = [
            ctypes.c_int, ctypes.POINTER(ctypes.c_char_p)]
        core.vim_runtime_instance_create.restype = ctypes.c_void_p
        core.vim_runtime_instance_wait.argtypes = [
            ctypes.c_void_p, wintypes.ULONG, ctypes.POINTER(ctypes.c_int)]
        core.vim_runtime_instance_wait.restype = ctypes.c_int
        core.vim_runtime_instance_destroy.argtypes = [ctypes.c_void_p]
        core.vim_runtime_instance_destroy.restype = ctypes.c_int

        def lines(name, suffix):
            return (directory / f"{name}.{suffix}").read_text(encoding="utf-8").splitlines()

        def start(name, interruptions):
            script = directory / f"{name}.vim"
            stop = directory / f"{name}.stop"
            script.write_text(
                "set nomore noswapfile\n"
                f"let g:owner = '{name}'\n"
                "let g:interruptions = 0\n"
                f"autocmd VimLeavePre * call writefile([g:owner], {quote(directory / (name + '.leave'))})\n"
                "function! ConsoleProbe()\n"
                f"  while g:interruptions < {interruptions} && !filereadable({quote(stop)})\n"
                "    try\n"
                f"      call writefile([g:owner, string(g:interruptions)], {quote(directory / (name + '.ready'))})\n"
                f"      while !filereadable({quote(stop)})\n"
                "        sleep 20m\n"
                "      endwhile\n"
                "    catch /^Vim:Interrupt$/\n"
                "      let g:interruptions += 1\n"
                f"      call writefile([g:owner, string(g:interruptions)], {quote(directory / (name + '.caught'))})\n"
                "    endtry\n"
                "  endwhile\n"
                "endfunction\n"
                "call ConsoleProbe()\n"
                f"call writefile([g:owner, string(g:interruptions)], {quote(directory / (name + '.result'))})\n"
                "qa!\n",
                encoding="utf-8",
            )
            # Non-silent Ex deliberately takes the real console path; -es would
            # bypass all console registration and produce a false-positive test.
            values = [b"vim", b"-e", b"-N", b"-u", b"NONE", b"-i", b"NONE",
                      b"-n", b"--log", str(directory / (name + ".vimlog")).encode("utf-8"),
                      b"-S", str(script).encode("utf-8")]
            argv = (ctypes.c_char_p * len(values))(*values)
            instance = core.vim_runtime_instance_create(len(values), argv)
            if not instance:
                raise AssertionError(f"Could not create console instance {name}")
            instances[name] = instance
            wait_until(lambda: lines(name, "ready"), lambda result: result == [name, "0"],
                       f"{name} entered its interruptible console loop")

        def finish(name, interruptions):
            status = ctypes.c_int()
            instance = instances[name]
            if core.vim_runtime_instance_wait(instance, 10000, ctypes.byref(status)) != 1:
                raise AssertionError(f"{name} did not finish after CtrlBreak")
            if status.value != 0:
                raise AssertionError(f"{name} exited with {status.value}")
            if lines(name, "result") != [name, str(interruptions)]:
                raise AssertionError(f"{name} observed the wrong console interruption count")
            if lines(name, "leave") != [name]:
                raise AssertionError(f"{name} did not execute its own leave hook")
            if core.vim_runtime_instance_destroy(instance) != 1:
                raise AssertionError(f"Could not destroy {name}")
            del instances[name]

        def interrupt():
            if not kernel.GenerateConsoleCtrlEvent(1, 0):  # CTRL_BREAK_EVENT
                raise ctypes.WinError(ctypes.get_last_error())

        try:
            start("A", 1)
            start("B", 2)
            if args.child == "fatal":
                (directory / "fatal-ready.json").write_text(
                    json.dumps({"window": int(kernel.GetConsoleWindow())}), encoding="utf-8")
                # The parent closes only this new console. Windows terminates
                # its attached process after the handler has preserved workers.
                time.sleep(30)
                raise AssertionError("Closing the probe console did not terminate its child")

            interrupt()
            finish("A", 1)
            wait_until(lambda: lines("B", "ready"), lambda result: result == ["B", "1"],
                       "B survived A and entered its second interruptible loop")
            if core.vim_runtime_instance_wait(instances["B"], 0, None) != 0:
                raise AssertionError("B stopped when A exited")
            interrupt()
            finish("B", 2)

            for cycle in range(args.fresh_cycles):
                name = f"C{cycle}"
                start(name, 1)
                interrupt()
                finish(name, 1)

            restored_modes = console_modes()
            # Vim explicitly enables the extended-flags bit when restoring input.
            expected_modes = [original_modes[0] | 0x80, original_modes[1]]
            if restored_modes != expected_modes:
                raise AssertionError(f"Console modes not restored: {restored_modes}, expected {expected_modes}")
            (directory / "passed.json").write_text(
                json.dumps({"fresh_cycles": args.fresh_cycles, "console_modes": restored_modes}),
                encoding="utf-8",
            )
        finally:
            for name in instances:
                (directory / f"{name}.stop").touch()
            for instance in instances.values():
                if core.vim_runtime_instance_wait(instance, 1000, None) == 1:
                    core.vim_runtime_instance_destroy(instance)


def run_child(args, directory: Path, mode: str) -> None:
    directory.mkdir()
    startup = subprocess.STARTUPINFO()
    startup.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    startup.wShowWindow = subprocess.SW_HIDE
    command = [sys.executable, str(Path(__file__).resolve()), "--child", mode,
               "--directory", str(directory), "--dll", str(args.dll),
               "--fresh-cycles", str(args.fresh_cycles)]
    with (directory / "child.log").open("w", encoding="utf-8") as log:
        process = subprocess.Popen(command, creationflags=subprocess.CREATE_NEW_CONSOLE,
                                   startupinfo=startup, stdout=log, stderr=log)
        try:
            if mode == "fatal":
                ready = wait_until(
                    lambda: json.loads((directory / "fatal-ready.json").read_text(encoding="utf-8")),
                    lambda result: bool(result.get("window")), "fatal child readiness", 25)
                user = ctypes.WinDLL("user32", use_last_error=True)
                user.PostMessageW.argtypes = [wintypes.HWND, wintypes.UINT,
                                             wintypes.WPARAM, wintypes.LPARAM]
                user.PostMessageW.restype = wintypes.BOOL
                if not user.PostMessageW(ready["window"], 0x10, 0, 0):  # WM_CLOSE
                    raise ctypes.WinError(ctypes.get_last_error())
            code = process.wait(timeout=25 + 12 * args.fresh_cycles)
            if mode == "regular":
                if code != 0 or not (directory / "passed.json").is_file():
                    raise AssertionError(f"Console child failed with exit code {code}")
            else:
                for name in ("A", "B"):
                    leave = directory / f"{name}.leave"
                    if not leave.is_file() or leave.read_text(encoding="utf-8").splitlines() != [name]:
                        raise AssertionError(
                            f"Fatal console close skipped {name}'s leave hook (child exit {code})")
                if (directory / "error.txt").exists():
                    raise AssertionError("Fatal console child reported an error")
        finally:
            if process.poll() is None:
                process.kill()
                process.wait(timeout=5)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dll", type=Path, default=DEFAULT_DLL)
    parser.add_argument("--fresh-cycles", type=int, default=3)
    parser.add_argument("--fatal", action="store_true",
                        help="also close a separate hidden console and verify both leave hooks")
    parser.add_argument("--child", choices=("regular", "fatal"), help=argparse.SUPPRESS)
    parser.add_argument("--directory", type=Path, help=argparse.SUPPRESS)
    args = parser.parse_args()
    if os.name != "nt":
        parser.error("This probe requires Windows")
    if args.fresh_cycles < 1:
        parser.error("--fresh-cycles must be positive")
    args.dll = args.dll.resolve()
    if not args.dll.is_file():
        parser.error(f"Build vim_shared_core first: {args.dll}")
    if args.child:
        try:
            child(args)
        except BaseException:
            (args.directory / "error.txt").write_text(traceback.format_exc(), encoding="utf-8")
            raise
        return

    with tempfile.TemporaryDirectory(prefix="vim-console-", dir=args.dll.parents[2],
                                     ignore_cleanup_errors=True) as temporary:
        directory = Path(temporary)
        try:
            run_child(args, directory / "regular", "regular")
            if args.fatal:
                run_child(args, directory / "fatal", "fatal")
        except BaseException:
            for report in directory.glob("*/error.txt"):
                print(report.read_text(encoding="utf-8"), file=sys.stderr)
            raise
    print(f"Console CtrlBreak reached both owners; B survived A; {args.fresh_cycles} fresh instances passed."
          + (" Fatal close ran both leave hooks." if args.fatal else ""))


if __name__ == "__main__":
    main()
