#!/usr/bin/env python3
"""Exercise actual Win32 input/resize routing for two handles in one DLL."""

import ctypes
import argparse
from ctypes import wintypes
import json
import os
from pathlib import Path
import tempfile
import time

ROOT = Path(__file__).resolve().parent.parent
DLL = ROOT / "build/vs2026-qt/Debug/vim/vimcore.dll"


def quote(path):
    return "'" + path.as_posix().replace("'", "''") + "'"


def require(condition, description):
    if not condition:
        raise AssertionError(description)


def until(read, accept, description):
    deadline = time.monotonic() + 8
    last = None
    while time.monotonic() < deadline:
        try:
            last = read()
            if accept(last):
                return last
        except (OSError, ValueError):
            pass  # A timer may be replacing the snapshot while it is read.
        time.sleep(0.02)
    raise AssertionError(f"{description}: last observation {last!r}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dll", type=Path, default=DLL)
    dll = parser.parse_args().dll.resolve()
    user32 = ctypes.WinDLL("user32", use_last_error=True)
    user32.PostMessageW.argtypes = [wintypes.HWND, wintypes.UINT,
                                   wintypes.WPARAM, wintypes.LPARAM]
    user32.PostMessageW.restype = wintypes.BOOL
    user32.SetWindowPos.argtypes = [wintypes.HWND, wintypes.HWND,
                                   ctypes.c_int, ctypes.c_int, ctypes.c_int,
                                   ctypes.c_int, wintypes.UINT]
    user32.SetWindowPos.restype = wintypes.BOOL
    with tempfile.TemporaryDirectory(prefix="vim-input-", dir=dll.parents[2],
                                     ignore_cleanup_errors=True) as temporary:
        directory = Path(temporary)
        with os.add_dll_directory(str(dll.parent)):
            core = ctypes.CDLL(str(dll))
            core.vim_runtime_instance_create.argtypes = [ctypes.c_int, ctypes.POINTER(ctypes.c_char_p)]
            core.vim_runtime_instance_create.restype = ctypes.c_void_p
            core.vim_runtime_instance_window.argtypes = [ctypes.c_void_p]
            core.vim_runtime_instance_window.restype = ctypes.c_void_p
            core.vim_runtime_instance_wait.argtypes = [ctypes.c_void_p, ctypes.c_ulong, ctypes.POINTER(ctypes.c_int)]
            core.vim_runtime_instance_destroy.argtypes = [ctypes.c_void_p]
            instances, windows = {}, {}

            def keys(name, text):
                for char in text:
                    if not user32.PostMessageW(windows[name], 0x102, ord(char), 1):
                        raise ctypes.WinError(ctypes.get_last_error())

            def snapshot(name, accept, description):
                return until(lambda: json.loads((directory / f"{name}.json").read_text(encoding="utf-8")),
                             accept, f"{name}: {description}")

            try:
                for name in ("A", "B"):
                    source = directory / f"{name}-文档.txt"
                    source.write_text(name + "-original\n", encoding="utf-8")
                    script = directory / f"{name}-配置.vim"
                    script.write_text(
                        "set nomore noswapfile guioptions=\n"
                        f"execute 'edit ' . fnameescape({quote(source)})\n"
                        "function! Snapshot(timer)\n"
                        "  let state = {'text': getline(1, '$'), 'mode': mode(1), "
                        "'cursor': getpos('.'), 'windows': winnr('$'), "
                        "'rows': &lines, 'columns': &columns, 'error': v:errmsg}\n"
                        f"  call writefile([json_encode(state)], {quote(directory / (name + '.json'))})\n"
                        "endfunction\n"
                        "call timer_start(30, function('Snapshot'), {'repeat': -1})\n"
                        f"autocmd VimLeavePre * call writefile(['{name}'], {quote(directory / (name + '.leave'))})\n",
                        encoding="utf-8")
                    args = ["vim", "-g", "-f", "-N", "-u", "NONE", "-U", "NONE",
                            "-i", "NONE", "-S", str(script)]
                    argv = (ctypes.c_char_p * len(args))(*(s.encode() for s in args))
                    instances[name] = core.vim_runtime_instance_create(len(args), argv)
                    if not instances[name]:
                        raise RuntimeError(f"Could not create {name}")
                for name in instances:
                    windows[name] = until(lambda: core.vim_runtime_instance_window(instances[name]),
                                          bool, f"{name} GUI ready")
                    snapshot(name, lambda s: s["text"] == [name + "-original"] and s["mode"] == "n",
                             "initial file and normal mode")

                keys("A", "iA-edit")
                snapshot("A", lambda s: s["mode"].startswith("i") and s["text"] == ["A-editA-original"], "insert mode")
                snapshot("B", lambda s: s["mode"] == "n" and s["text"] == ["B-original"], "unaffected by A input")
                keys("B", "iB-edit")
                snapshot("B", lambda s: s["mode"].startswith("i") and s["text"] == ["B-editB-original"], "independent insert mode")
                keys("A", "\x1bu")
                snapshot("A", lambda s: s["mode"] == "n" and s["text"] == ["A-original"], "undo")
                snapshot("B", lambda s: s["mode"].startswith("i") and s["text"] == ["B-editB-original"], "insert mode survives A undo")
                keys("A", "\x12:vsplit\r")
                snapshot("A", lambda s: s["windows"] == 2 and s["text"] == ["A-editA-original"], "redo and vertical split")
                keys("B", "\x1b:split\r")
                snapshot("B", lambda s: s["windows"] == 2 and s["mode"] == "n", "horizontal split")

                before = {name: snapshot(name, lambda s: True, "before resize") for name in instances}
                for name, width, height in (("A", 640, 480), ("B", 960, 640)):
                    if not user32.SetWindowPos(windows[name], None, 0, 0, width, height, 0x16):
                        raise ctypes.WinError(ctypes.get_last_error())
                a = snapshot("A", lambda s: (s["columns"], s["rows"]) !=
                             (before["A"]["columns"], before["A"]["rows"]), "A viewport changed")
                b = snapshot("B", lambda s: (s["columns"], s["rows"]) !=
                             (before["B"]["columns"], before["B"]["rows"]) and
                             s["columns"] > a["columns"] and s["rows"] > a["rows"], "B independent viewport changed")
                require(not a["error"] and not b["error"], (a, b))

                keys("A", ":wqa\r")
                status = ctypes.c_int(-999)
                require(core.vim_runtime_instance_wait(instances["A"], 8000, ctypes.byref(status)) == 1, "A did not exit")
                require(status.value == 0, f"A exit status {status.value}")
                require((directory / "A.leave").read_text().strip() == "A", "A leave hook")
                require(core.vim_runtime_instance_wait(instances["B"], 0, None) == 0, "B exited with A")
                keys("B", "A-survivor-继续\x1b")
                snapshot("B", lambda s: s["mode"] == "n" and s["text"] == ["B-editB-original-survivor-继续"], "Unicode editing after A exits")
                keys("B", ":wqa\r")
                require(core.vim_runtime_instance_wait(instances["B"], 8000, ctypes.byref(status)) == 1, "B did not exit")
                require(status.value == 0, f"B exit status {status.value}")
                require((directory / "B.leave").read_text().strip() == "B", "B leave hook")
                require((directory / "A-文档.txt").read_text(encoding="utf-8").strip() == "A-editA-original", "A saved text")
                require((directory / "B-文档.txt").read_text(encoding="utf-8").strip() == "B-editB-original-survivor-继续", "B saved text")
            finally:
                unfinished = []
                for name, instance in instances.items():
                    if instance:
                        if core.vim_runtime_instance_wait(instance, 0, None) == 0 and name in windows:
                            keys(name, "\x1b:qa!\r")
                            core.vim_runtime_instance_wait(instance, 8000, None)
                        if core.vim_runtime_instance_destroy(instance) != 1:
                            unfinished.append(name)
                if unfinished:
                    raise RuntimeError(f"Could not clean up GUI instances: {unfinished}")
    print("Two handles passed native input, concurrent modes, undo/redo, split, resize, save and survivor editing.")


if __name__ == "__main__":
    main()
