"""Exercise the queued wide-path GUI open API in a real Vim worker."""

import argparse
import ctypes
from ctypes import wintypes
import json
import os
from pathlib import Path
import tempfile
import time


def quote(path: Path) -> str:
    return "'" + path.as_posix().replace("'", "''") + "'"


def normalized(path: str | Path) -> str:
    return os.path.normcase(os.path.normpath(str(path))).replace("\\", "/")


def until(read, accept, description: str):
    deadline = time.monotonic() + 12
    last = None
    while time.monotonic() < deadline:
        try:
            last = read()
            if accept(last):
                return last
        except (OSError, ValueError):
            pass
        time.sleep(0.02)
    raise AssertionError(f"{description}: last observation {last!r}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dll", type=Path, required=True)
    options = parser.parse_args()
    dll = options.dll.resolve()
    with tempfile.TemporaryDirectory(prefix="vim-open-api-", dir=dll.parents[2]) as temporary:
        directory = Path(temporary)
        first = directory / "first # % 中文.txt"
        second = directory / "second [brackets] 空格.txt"
        first.write_text("first contents\n", encoding="utf-8")
        second.write_text("second contents\n", encoding="utf-8")
        state = directory / "state.json"
        read_log = directory / "read.log"
        script = directory / "probe.vim"
        script.write_text(
            "set nomore noswapfile guioptions=\n"
            "function! Snapshot(timer)\n"
            "  let state = {'file': expand('%:p'), 'text': getline(1, '$')}\n"
            f"  call writefile([json_encode(state)], {quote(state)})\n"
            "endfunction\n"
            "call timer_start(30, function('Snapshot'), {'repeat': -1})\n"
            f"autocmd BufReadPost * call writefile([expand('<afile>:p')], {quote(read_log)}, 'a')\n",
            encoding="utf-8",
        )
        with os.add_dll_directory(str(dll.parent)):
            core = ctypes.CDLL(str(dll))
            core.vim_runtime_instance_create.argtypes = [ctypes.c_int, ctypes.POINTER(ctypes.c_char_p)]
            core.vim_runtime_instance_create.restype = ctypes.c_void_p
            core.vim_runtime_instance_window.argtypes = [ctypes.c_void_p]
            core.vim_runtime_instance_window.restype = ctypes.c_void_p
            core.vim_runtime_instance_open_file_w.argtypes = [ctypes.c_void_p, ctypes.c_wchar_p]
            core.vim_runtime_instance_open_file_w.restype = ctypes.c_int
            core.vim_runtime_instance_request_close.argtypes = [ctypes.c_void_p]
            core.vim_runtime_instance_request_close.restype = ctypes.c_int
            core.vim_runtime_instance_wait.argtypes = [ctypes.c_void_p, ctypes.c_ulong, ctypes.POINTER(ctypes.c_int)]
            core.vim_runtime_instance_wait.restype = ctypes.c_int
            core.vim_runtime_instance_destroy.argtypes = [ctypes.c_void_p]
            core.vim_runtime_instance_destroy.restype = ctypes.c_int
            args = ["vim", "-g", "-f", "-N", "-u", "NONE", "-U", "NONE", "-i", "NONE", "-S", str(script)]
            argv = (ctypes.c_char_p * len(args))(*(arg.encode("utf-8") for arg in args))
            instance = core.vim_runtime_instance_create(len(args), argv)
            assert instance, "Could not create Vim GUI instance"
            try:
                until(lambda: core.vim_runtime_instance_window(instance), bool, "GUI HWND did not appear")
                assert core.vim_runtime_instance_open_file_w(instance, None) == -1
                assert core.vim_runtime_instance_open_file_w(instance, str(first)) == 1
                assert core.vim_runtime_instance_open_file_w(instance, str(second)) == 1
                current = until(
                    lambda: json.loads(state.read_text(encoding="utf-8")),
                    lambda value: normalized(value["file"]) == normalized(second)
                    and value["text"] == ["second contents"],
                    "second Unicode path was not opened",
                )
                log = until(
                    lambda: read_log.read_text(encoding="utf-8").splitlines(),
                    lambda value: len(value) >= 2,
                    "the two file opens were not dispatched in order",
                )
                assert [normalized(value) for value in log[:2]] == [normalized(first), normalized(second)], log
                assert current["text"] == ["second contents"]
                assert core.vim_runtime_instance_request_close(instance) == 1
                status = ctypes.c_int(-1)
                assert core.vim_runtime_instance_wait(instance, 8000, ctypes.byref(status)) == 1
                assert status.value == 0, status.value
            finally:
                if core.vim_runtime_instance_wait(instance, 0, None) == 0:
                    core.vim_runtime_instance_request_close(instance)
                    core.vim_runtime_instance_wait(instance, 8000, None)
                assert core.vim_runtime_instance_destroy(instance) == 1
    print("Queued wide-path file opens preserved Unicode, special characters and FIFO order.")


if __name__ == "__main__":
    main()
