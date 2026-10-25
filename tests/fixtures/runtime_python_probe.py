"""Shared Python plugin used by the Qt host's two-instance regression.

Python module globals are deliberately process-wide. Vim objects are not.
"""

import gc
import threading
from pathlib import Path
import vim

if not __debug__:
    raise RuntimeError("Run the Python plugin regression without PYTHONOPTIMIZE")

owners = {}
deferred = {}


def text(value):
    return value.decode() if isinstance(value, bytes) else value


def start():
    name = vim.eval("g:qt_instance")
    vim.vars["python_dictionary_owner"] = name
    assert {"vars", "vvars", "options"}.issubset(dir(vim))
    imported = {}
    exec("from vim import *", imported)
    assert text(imported["vars"]["python_dictionary_owner"]) == name
    vim.current.buffer.vars["python_buffer_owner"] = name
    vim.command("function! PyProbeOwner()\nreturn g:qt_instance\nendfunction")
    objects = {
        "dict": vim.vars,
        "list": vim.List([name]),
        "tuple": vim.Tuple([name]),
        "function": vim.Function("PyProbeOwner"),
        "buffer": vim.current.buffer,
        "window": vim.current.window,
        "tabpage": vim.current.tabpage,
        "options": vim.options,
        "range": vim.current.buffer.range(0, 0),
        "dict_iterator": iter(vim.vars),
        "list_iterator": iter(vim.List([name])),
    }
    owners[name] = objects

    # Exercise foreign final-decref, including the Python subclass path.
    class PluginDictionary(vim.Dictionary):
        pass

    deferred[name] = [vim.Dictionary({"owner": name}), PluginDictionary({"owner": name})]
    errors = []

    def foreign_thread():
        for action in (lambda: vim.eval("g:qt_instance"),
                       lambda: vim.vars, lambda: vim.current.buffer):
            try:
                action()
            except RuntimeError:
                continue
            errors.append("Python-created thread accessed Vim without an owner")

    thread = threading.Thread(target=foreign_thread)
    thread.start()
    thread.join(2)
    assert not thread.is_alive() and not errors, errors


def assert_foreign(objects):
    operations = {
        "dict": lambda obj: len(obj),
        "list": lambda obj: len(obj),
        "tuple": lambda obj: len(obj),
        "function": lambda obj: obj(),
        "buffer": lambda obj: obj[0],
        "window": lambda obj: obj.height,
        "tabpage": lambda obj: obj.number,
        "options": lambda obj: obj["ignorecase"],
        "range": lambda obj: len(obj),
        "dict_iterator": lambda obj: next(obj),
        "list_iterator": lambda obj: next(obj),
    }
    for kind, obj in objects.items():
        try:
            operations[kind](obj)
        except RuntimeError:
            continue
        raise AssertionError(f"foreign or expired {kind} was accepted")


def callback():
    name = vim.eval("g:qt_instance")
    output = vim.eval("""execute("python3 print('python-route-' + vim.eval('g:qt_instance'))")""")
    assert "python-route-" + name in output
    assert "python-route-" + ("B" if name == "A" else "A") not in output
    assert text(vim.vars["python_dictionary_owner"]) == name
    assert text(vim.current.buffer.vars["python_buffer_owner"]) == name
    assert text(owners[name]["function"]()) == name
    assert vim.vvars["version"] >= 900
    vim.options["ignorecase"] = name == "B"
    assert bool(vim.options["ignorecase"]) == (name == "B")
    if name == "B" and "A" in owners:
        assert_foreign(owners["A"])
        deferred.pop("A", None)
        gc.collect()
    vim.vars["python_plugin_checked"] = name


def after_a():
    assert vim.eval("g:qt_instance") == "B"
    assert_foreign(owners.pop("A"))
    gc.collect()
    callback()


def quit_instance():
    mode = text(vim.vars["python_quit_mode"])
    path = text(vim.vars["python_finally_path"])
    try:
        if mode in ("command", "pydo"):
            vim.command("qa!")
        elif mode == "option":
            vim.command("autocmd OptionSet ignorecase qa!")
            vim.options["ignorecase"] = not vim.options["ignorecase"]
        else:
            vim.command("function! QuitProbe()\nqa!\nendfunction")
            if mode == "function":
                vim.Function("QuitProbe")()
            elif mode == "eval":
                vim.eval("QuitProbe()")
            elif mode == "bindeval":
                vim.bindeval("QuitProbe()")
            else:
                raise AssertionError(f"Unknown quit probe: {mode}")
    finally:
        Path(path).write_text("A\n", encoding="utf-8")
