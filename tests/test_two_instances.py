#!/usr/bin/env python3
"""Run two silent Ex Vim instances in one loaded vimcore.dll.

This is an integration probe for the early C ABI.  It intentionally exercises
overlapping lifetimes and several Vim-owned values; the full GUI/plugin gate is
tracked separately in docs/dual-instance-runtime.md.
"""

from __future__ import annotations

import ctypes
import argparse
from pathlib import Path
import tempfile
import time
import subprocess


ROOT = Path(__file__).resolve().parent.parent
DLL = ROOT / "build/vs2026-qt/Debug/vim/vimcore.dll"


def vim_quote(path: Path) -> str:
    return "'" + path.as_posix().replace("'", "''") + "'"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dll", type=Path, default=DLL)
    parser.add_argument("--single", action="store_true", help="diagnose one instance")
    parser.add_argument("--debug-break-on-slow-start", action="store_true")
    parser.add_argument("--async", dest="check_async", action="store_true")
    parser.add_argument("--terminal", action="store_true")
    parser.add_argument("--fresh-cycles", type=int, default=1,
                        help="repeat creation and cleanup of the fresh C handle")
    parser.add_argument("--compare-standalone", action="store_true",
                        help="run the same scripts with the matching standalone executable")
    args = parser.parse_args()
    dll = args.dll.resolve()
    if args.fresh_cycles < 1:
        parser.error("--fresh-cycles must be positive")
    if not dll.is_file():
        raise SystemExit(f"Build vim_shared_core first: {dll}")

    with tempfile.TemporaryDirectory(
        prefix="vim-two-instances-", dir=ROOT / "build/vs2026-qt",
        ignore_cleanup_errors=True,
    ) as temporary:
        directory = Path(temporary)
        plugin_directory = directory / "plugin"
        plugin_directory.mkdir()
        (plugin_directory / "probe.vim").write_text(
            "let g:probe_plugin_loaded = get(g:, 'probe_plugin_loaded', 0) + 1\n"
            "let g:probe_plugin_marker = g:instance_marker\n"
            "augroup DualInstanceProbe\n"
            "  autocmd!\n"
            "  autocmd User DualInstanceProbe let g:probe_event_marker = g:instance_marker\n"
            "  autocmd VimLeavePre * call writefile([g:instance_marker], g:probe_leave_path)\n"
            "augroup END\n",
            encoding="utf-8",
        )
        (plugin_directory / "probe9.vim").write_text(
            "vim9script\n"
            "var owner: string = g:instance_marker\n"
            "def g:ProbeVim9(): string\n"
            "  return owner\n"
            "enddef\n"
            "defcompile\n", encoding="utf-8")
        scripts = []
        expected = {}
        expected_terminal_rows = {}
        targets = (("A", 3),) if args.single else (("A", 3), ("B", 7), ("C", 5))
        for name, tabstop in targets:
            script = directory / f"{name}.vim"
            vimrc = directory / f"{name}.vimrc"
            started = directory / f"{name}.started"
            result = directory / f"{name}.result"
            vimrc.write_text(
                "set nocompatible\n"
                f"let g:instance_marker = '{name}'\n"
                f"let g:probe_leave_path = {vim_quote(directory / (name + '.leave'))}\n"
                f"execute 'set runtimepath^=' . fnameescape({vim_quote(directory)})\n"
                "set loadplugins\n",
                encoding="utf-8",
            )
            if args.check_async:
                async_script = (
                    "function! ProbeOut(path, channel, message)\n"
                    "  call writefile([g:instance_marker, a:message], a:path)\n"
                    "endfunction\n"
                    "function! ProbeExit(path, job, status)\n"
                    "  call writefile([g:instance_marker, string(a:status)], a:path)\n"
                    "endfunction\n"
                    f"call timer_start(100, {{-> writefile([g:instance_marker], {vim_quote(directory / (name + '.timer'))})}})\n"
                    f"let g:probe_job = job_start(['cmd', '/c', 'echo', '{name}'], "
                    f"{{'out_cb': function('ProbeOut', [{vim_quote(directory / (name + '.job'))}]), "
                    f"'exit_cb': function('ProbeExit', [{vim_quote(directory / (name + '.exit'))}]), 'err_io': 'null'}})\n"
                )
            else:
                async_script = ""
            term_rows = tabstop + 3
            expected_terminal_rows[name] = term_rows
            if args.terminal:
                terminal_script = (
                    f"let g:probe_term = term_start(['cmd', '/c', 'echo', '{name}'], "
                    f"{{'hidden': 1, 'term_rows': {term_rows}, 'term_cols': 40}})\n"
                    "if g:probe_term <= 0 | cquit 4 | endif\n"
                )
                terminal_result = (
                    "let s:terminal_tries = 0\n"
                    f"while trim(term_getline(g:probe_term, 1)) != '{name}' && s:terminal_tries < 100\n"
                    "  call term_wait(g:probe_term, 50)\n"
                    "  let s:terminal_tries += 1\n"
                    "endwhile\n"
                    f"call writefile([string(len(term_list())), "
                    f"string(term_getsize(g:probe_term)), trim(term_getline(g:probe_term, 1))], "
                    f"{vim_quote(directory / (name + '.terminal'))})\n"
                )
            else:
                terminal_script = ""
                terminal_result = ""
            if name == "A" and not args.single:
                wait_script = (
                    f"let s:partner = {vim_quote(directory / 'B.started')}\n"
                    "let s:tries = 0\n"
                    "while !filereadable(s:partner) && s:tries < 400\n"
                    "  sleep 50m\n"
                    "  let s:tries += 1\n"
                    "endwhile\n"
                    "if !filereadable(s:partner) | cquit 2 | endif\n"
                    "sleep 300m\n"
                )
            elif name == "B":
                wait_script = (
                    f"let s:release = {vim_quote(directory / 'B.release')}\n"
                    "let s:tries = 0\n"
                    "while !filereadable(s:release) && s:tries < 400\n"
                    "  sleep 50m\n"
                    "  let s:tries += 1\n"
                    "endwhile\n"
                    "if !filereadable(s:release) | cquit 3 | endif\n"
                )
            else:
                wait_script = "sleep 300m\n"
            if args.check_async:
                if name == "B":
                    # B.release is written only after the host destroys A.
                    wait_script += (
                        "let g:survivor_job = job_start(['cmd', '/c', 'echo', 'B-after-A'], "
                        f"{{'out_cb': function('ProbeOut', [{vim_quote(directory / 'B.after-a-job')}]), "
                        f"'exit_cb': function('ProbeExit', [{vim_quote(directory / 'B.after-a-exit')}]), 'err_io': 'null'}})\n"
                        "let s:survivor_tries = 0\n"
                        f"while (!filereadable({vim_quote(directory / 'B.after-a-job')}) || "
                        f"!filereadable({vim_quote(directory / 'B.after-a-exit')})) && s:survivor_tries < 100\n"
                        "  sleep 50m\n"
                        "  let s:survivor_tries += 1\n"
                        "endwhile\n"
                    )
                wait_script += (
                    "let s:job_tries = 0\n"
                    f"while (getfsize({vim_quote(directory / (name + '.job'))}) <= 0 || "
                    f"!filereadable({vim_quote(directory / (name + '.exit'))})) && s:job_tries < 100\n"
                    "  sleep 50m\n"
                    "  let s:job_tries += 1\n"
                    "endwhile\n"
                    f"call writefile([string(job_info(g:probe_job)), "
                    f"job_status(g:probe_job), v:errmsg], "
                    f"{vim_quote(directory / (name + '.job-status'))})\n"
                )
            script.write_text(
                "doautocmd User DualInstanceProbe\n"
                "filetype plugin indent on\n"
                "syntax on\n"
                "setfiletype vim\n"
                f"let @a = '{name}'\n"
                f"set tabstop={tabstop}\n"
                f"call setline(1, ['{name}-first', '{name}-second'])\n"
                "execute 'nnoremap <F6> ' . g:instance_marker\n"
                "let g:probe_map = maparg('<F6>', 'n')\n"
                "execute 'command! ProbeCmd let g:probe_command = \"' . g:instance_marker . '\"'\n"
                "call cursor(2, 2)\n"
                "let g:probe_cursor = printf('%d:%d', line('.'), col('.'))\n"
                "call setline(1, g:instance_marker . '-edited')\n"
                "undo\n"
                "let g:probe_undo = getline(1)\n"
                "redo\n"
                "let g:probe_redo = getline(1)\n"
                "call setline(1, g:instance_marker . '-first')\n"
                "let @/ = g:instance_marker .. '-first'\n"
                "split\n"
                "tabnew\n"
                "call setline(1, g:instance_marker . '-tab')\n"
                "tabprevious\n"
                f"call writefile(['started'], {vim_quote(started)})\n"
                + async_script
                + terminal_script
                + wait_script
                + terminal_result
                +
                "ProbeCmd\n"
                f"call writefile([g:instance_marker, @a, string(&tabstop), "
                f"string(winnr('$')), getline(1), g:probe_plugin_marker, "
                f"string(g:probe_plugin_loaded), g:probe_event_marker, @/, "
                f"g:probe_map, g:probe_cursor, g:probe_undo, g:probe_redo, "
                f"g:probe_command, ProbeVim9(), get(b:, 'current_syntax', 'missing'), "
                f"string(tabpagenr('$')), getbufline(tabpagebuflist(2)[0], 1)[0]], "
                f"{vim_quote(result)})\n"
                "qa!\n",
                encoding="utf-8",
            )
            scripts.append(script)
            expected[name] = (result, [name, name, str(tabstop), "2",
                                       f"{name}-first", name, "1", name,
                                       f"{name}-first", name, "2:2",
                                       "", f"{name}-edited", name, name, "vim", "2", f"{name}-tab"])

        with __import__("os").add_dll_directory(str(dll.parent)):
            core = ctypes.CDLL(str(dll))
            core.vim_runtime_instance_create.argtypes = [
                ctypes.c_int,
                ctypes.POINTER(ctypes.c_char_p),
            ]
            core.vim_runtime_instance_create.restype = ctypes.c_void_p
            core.vim_runtime_instance_wait.argtypes = [
                ctypes.c_void_p,
                ctypes.c_ulong,
                ctypes.POINTER(ctypes.c_int),
            ]
            core.vim_runtime_instance_wait.restype = ctypes.c_int
            core.vim_runtime_instance_destroy.argtypes = [ctypes.c_void_p]
            core.vim_runtime_instance_destroy.restype = ctypes.c_int

            instances = []
            try:
                for script in scripts[:1 if args.single else 2]:
                    vimrc = script.with_suffix(".vimrc")
                    argv = [b"vim", b"-e", b"-s", b"-N", b"-u", str(vimrc).encode("utf-8"), b"-i", b"NONE", b"-S", str(script).encode("utf-8")]
                    arguments = (ctypes.c_char_p * len(argv))(*argv)
                    instance = core.vim_runtime_instance_create(len(argv), arguments)
                    if not instance:
                        raise RuntimeError(f"create failed for {script.name}")
                    instances.append(instance)

                if args.debug_break_on_slow_start:
                    deadline = time.monotonic() + 5
                    while time.monotonic() < deadline:
                        if (directory / "A.started").is_file() and (directory / "B.started").is_file():
                            break
                        time.sleep(0.05)
                    else:
                        print("Slow startup:", sorted(path.name for path in directory.glob("*")), flush=True)
                        ctypes.WinDLL("kernel32").DebugBreak()

                for index, instance in enumerate(instances):
                    status = ctypes.c_int(-999)
                    if core.vim_runtime_instance_wait(instance, 30000, ctypes.byref(status)) != 1:
                        raise RuntimeError("instance did not exit within 30 seconds")
                    if status.value != 0:
                        raise RuntimeError(f"Vim exited with {status.value}")
                    if index == 0 and len(instances) == 2:
                        if core.vim_runtime_instance_wait(instances[1], 0, None) != 0:
                            raise AssertionError("B exited before A was closed")
                        if core.vim_runtime_instance_destroy(instance) != 1:
                            raise RuntimeError("A could not be destroyed while B was running")
                        instances[0] = None
                        (directory / "B.release").write_text("continue\n", encoding="utf-8")
                if not args.single:
                    script = scripts[2]
                    vimrc = script.with_suffix(".vimrc")
                    argv = [b"vim", b"-e", b"-s", b"-N", b"-u", str(vimrc).encode("utf-8"), b"-i", b"NONE", b"-S", str(script).encode("utf-8")]
                    arguments = (ctypes.c_char_p * len(argv))(*argv)
                    for cycle in range(args.fresh_cycles):
                        for suffix in ("result", "leave", "job", "exit", "timer", "terminal"):
                            (directory / f"C.{suffix}").unlink(missing_ok=True)
                        instance = core.vim_runtime_instance_create(len(argv), arguments)
                        if not instance:
                            raise RuntimeError(f"create failed for fresh C cycle {cycle + 1}")
                        instances.append(instance)
                        status = ctypes.c_int(-999)
                        if core.vim_runtime_instance_wait(instance, 10000, ctypes.byref(status)) != 1 or status.value != 0:
                            raise RuntimeError(f"fresh cycle {cycle + 1} failed: exit status {status.value}")
                        if not (directory / "C.result").is_file() or not (directory / "C.leave").is_file():
                            raise AssertionError(f"fresh cycle {cycle + 1} omitted result or leave hook")
                        if core.vim_runtime_instance_destroy(instance) != 1:
                            raise RuntimeError(f"fresh cycle {cycle + 1} could not be destroyed")
                        instances[-1] = None
            finally:
                print("Probe files:", sorted(path.name for path in directory.glob("*")))
                if args.check_async:
                    print("Async values:", [(path.name, path.read_text(errors="replace"))
                                           for path in sorted(directory.glob("*.timer"))
                                           + sorted(directory.glob("*.job"))])
                    print("Job status:", [(path.name, path.read_text(errors="replace"))
                                          for path in sorted(directory.glob("*.job-status"))])
                if args.terminal:
                    print("Terminal values:", [(path.name, path.read_text(errors="replace"))
                                               for path in sorted(directory.glob("*.terminal"))])
                for instance in instances:
                    if instance:
                        core.vim_runtime_instance_destroy(instance)

        for name, (result, wanted) in expected.items():
            if not result.is_file():
                raise AssertionError(f"{name} did not write a result")
            actual = result.read_text(encoding="utf-8").splitlines()
            if actual != wanted:
                raise AssertionError(f"{name}: expected {wanted!r}, got {actual!r}")
            leave = directory / f"{name}.leave"
            if not leave.is_file() or leave.read_text(encoding="utf-8").splitlines() != [name]:
                raise AssertionError(f"{name} plugin leave hook was not isolated")
            if args.check_async:
                for suffix, contents in (("timer", [name]), ("job", [name, name]), ("exit", [name, "0"])):
                    path = directory / f"{name}.{suffix}"
                    if not path.is_file() or path.read_text(encoding="utf-8").splitlines() != contents:
                        raise AssertionError(f"{name} {suffix} callback/output was not isolated")
                if name == "B":
                    for suffix, contents in (("job", ["B", "B-after-A"]), ("exit", ["B", "0"])):
                        path = directory / f"B.after-a-{suffix}"
                        if not path.is_file() or path.read_text(encoding="utf-8").splitlines() != contents:
                            raise AssertionError(f"B {suffix} callback failed after A was destroyed")
            if args.terminal:
                terminal = directory / f"{name}.terminal"
                if not terminal.is_file() or terminal.read_text(encoding="utf-8").splitlines() != [
                    "1", f"[{expected_terminal_rows[name]}, 40]", name
                ]:
                    raise AssertionError(f"{name} terminal buffer was not isolated")
        if args.compare_standalone:
            executable = dll.with_name("vimd.exe" if dll.parent.parent.name == "Debug" else "vim.exe")
            for script in scripts:
                name = script.stem
                suffixes = ["result", "leave"]
                if args.check_async:
                    suffixes += ["timer", "job", "exit"]
                    if name == "B":
                        suffixes += ["after-a-job", "after-a-exit"]
                if args.terminal:
                    suffixes += ["terminal"]
                reference = {suffix: (directory / f"{name}.{suffix}").read_text(encoding="utf-8")
                             for suffix in suffixes}
                for suffix in suffixes:
                    (directory / f"{name}.{suffix}").unlink()
                completed = subprocess.run(
                    [str(executable), "-e", "-s", "-N", "-u", str(script.with_suffix(".vimrc")),
                     "-i", "NONE", "-S", str(script)],
                    timeout=30, capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
                if completed.returncode:
                    raise AssertionError(f"Standalone {name} exited with {completed.returncode}: {completed.stderr!r}")
                for suffix, expected_text in reference.items():
                    path = directory / f"{name}.{suffix}"
                    if not path.is_file() or path.read_text(encoding="utf-8") != expected_text:
                        raise AssertionError(f"Standalone {name}.{suffix} differs from the DLL result")
            print("Standalone executable produced the same editing, plugin and async results.")
        print(f"Two overlapping Vim handles isolated state; fresh C completed {args.fresh_cycles} cycle(s).")


if __name__ == "__main__":
    main()
