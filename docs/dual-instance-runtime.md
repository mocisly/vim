# Two Vim instances in one Windows DLL

`vimcore.dll` exposes independent opaque Vim handles in one host process. Each handle runs the existing Vim core, including Vimscript/Vim9, buffers, splits, tabs, plugins, timers, jobs, channels and terminal buffers. The Qt host embeds the native GUI window belonging to each handle. No copied DLL images or helper Vim processes are used for engine isolation.

## Ownership and accepted boundary

Every instance has one dedicated CRT worker thread. Vim-owned mutable globals, file statics and function statics use `VIM_INSTANCE_TLS` / `VIM_GUI_TLS` in the runtime build. The standalone build keeps its original storage. This includes editor state, option tables, script/function storage, input/undo, screen and mouse state, asynchronous callbacks, GUI resources and dynamic terminal backends. The internal buffer/window context is only one part of this state; switching it alone does not switch an instance.

The host must serialize **all API operations on a given handle**, and must not call internal Vim functions from the Qt thread or another worker. Different handles may run concurrently. An instance cannot migrate between threads. Each worker reserves the same 8 MiB stack as the standalone target, independently of the host's default. Retain the DLL until every worker has exited and every handle has been destroyed. Native window handles are borrowed and expire on exit. The Qt host creates two native panes first and passes each pane's HWND through Vim's `--windowid` option; Vim parents each GUI window before showing it, so startup does not expose a separate top-level Vim window.

The acceptance boundary is independent **Vim-managed state**. Process resources remain shared: the Windows clipboard and console, current working directory, environment, CPython interpreter and imported Python modules. Consequently, `:cd`, environment changes and ordinary Python module globals can affect the process. Native plugin side effects and crashes are not isolated. Use absolute paths and coordinate process services when embedding in a larger application.

Python command globals are instance-owned. `vim.vars`, `vim.vvars`, `vim.options` and `vim.current` resolve against the executing worker. Captured Vim wrappers remain owned by their original instance: using one from another worker, from a Python-created thread without a Vim owner, or after its instance exits raises an error. Foreign final decrefs are routed to the owning worker; teardown invalidates surviving wrappers before Vim's state is freed. Python modules are shared, so a plugin should keep its instance data in Vim or key its own Python state explicitly. An embedding host that has already initialized CPython is not currently a supported Python integration configuration.

## C ABI and lifecycle

The declarations are in `include/vim_runtime_api.h`:

| Operation | Contract |
| --- | --- |
| `vim_runtime_instance_create` | Copy arguments and start one worker; return an opaque handle or NULL. |
| `vim_runtime_instance_window` | Return the ready native GUI HWND, or NULL. |
| `vim_runtime_instance_request_close` | Post normal GUI close; Vim may ask to save or cancel. |
| `vim_runtime_instance_wait` | Return 1 when exited, 0 on timeout, -1 on error; optionally return Vim's exit code. |
| `vim_runtime_instance_destroy` | Release an exited handle; return 0 while it is still running. |

GUI input, focus and resizing use the native view and its Windows message queue. There is no general non-GUI input/state-inspection API yet. Ex sessions can execute startup scripts; console sessions use the process console. The Qt UI never directly enters the Vim core. Closing one pane completes that instance's leave hooks and cleanup while the other pane remains usable. Cancelling a close leaves the host open, and a later close starts a new attempt.

The shared target enables `EXITFREE`. Shutdown releases Vim-owned storage, GUI/DLL resources and Python wrapper references before the worker terminates. Windows console callbacks record events and wake registered workers; only an owning worker touches Vim state. The last console instance restores the host's original console mode. Windows shutdown still ends the host process according to operating-system policy.

## Build

The `vs2026-qt` preset matches WetWeather's Windows toolchain: CMake 4.2+, Visual Studio 18 2026 x64, MSVC 19.50+, the compiler's latest C++ mode and Qt 6.12 Core/Gui/Widgets. Qt is deployed beside the host with `windeployqt`; the full `upstream/vim/runtime/` tree is copied beside both build configurations. Our CMake modules, API, host, tests, and optional local assets are outside the upstream tree.

```powershell
cmake --preset vs2026-qt
cmake --build build/vs2026-qt --config Debug --target vim_qt_host vim --parallel 8
& build/vs2026-qt/Debug/vim/vim_qt_host.exe
```

Normal host launches load regular Vim configuration. The Ex regression uses separate vimrc files and normally auto-loaded Vimscript and Vim9 plugins. GUI regressions use deterministic startup scripts without user configuration.

## Regression evidence

Validation completed on 2026-10-25: both Debug and Release build the runtime
DLL, Qt host and standalone executable successfully. The complete suite below
passes in both configurations, with five fresh-instance cycles per driver.
The final source diff check and Python driver syntax checks also pass.

Run the complete suite against a built configuration:

```powershell
python tests/test_runtime.py --configuration Debug
python tests/test_runtime.py --configuration Release
```

This includes the following individual drivers and six Python-initiated exit variants (command, function, eval, bindeval, option callback and py3do). Each exit variant requires Python's `finally` block to run and B to execute Python after the host has destroyed A's handle.

```powershell
python tests/test_two_instances.py --async --terminal --fresh-cycles 5 --compare-standalone
python tests/test_gui_instances.py
python tests/test_gui_input.py
python tests/test_console_instances.py --fresh-cycles 5 --fatal
& build/vs2026-qt/Debug/vim/vim_qt_host.exe --self-test
& build/vs2026-qt/Debug/vim/vim_qt_host.exe --self-test-close-retry
& build/vs2026-qt/Debug/vim/vim_qt_host.exe --self-test-python
```

The Python Qt probe requires the configured Python 3.14 DLL on the loader path. To test another configuration, pass `--dll <path-to-vimcore.dll>` to the Python drivers and run the matching Qt executable.

| Requirement | Regression |
| --- | --- |
| One DLL, concurrent A/B, fresh C | `test_two_instances.py`, repeated create/wait/destroy |
| Independent editing, modes, undo/redo, splits, resize | `test_gui_input.py`, actual WM_CHAR and native resize messages |
| Direct startup inside the Qt panes | Qt self-test checks both Vim windows have their expected native parent before attaching them |
| Unicode filenames and text | `test_gui_input.py` |
| Registers, mappings, options, search, commands, autocommands | `test_two_instances.py` |
| Automatic Vimscript/Vim9 plugin loading, syntax and filetype runtime | `test_two_instances.py` |
| Timer, channel output, job exit and terminal text ownership | `test_two_instances.py --async --terminal` |
| B callbacks and editing after A is destroyed | Ex and GUI input drivers |
| Corresponding standalone behavior | `--compare-standalone`, identical scripts and result comparison |
| Actual imported Python plugin and wrapper lifetimes | Qt `--self-test-python`, `tests/fixtures/runtime_python_probe.py` |
| Cancelled close followed by successful retry | Qt `--self-test-close-retry` |
| Console interrupt dispatch, survivor and mode restoration | `test_console_instances.py` |

`tools/audit_instance_state.py` inventories writable named COFF symbols, including COMMON symbols and TLS, from the actual shared target. Remaining ordinary symbols include lookup tables and coordinated process services. The audit is a review aid, not a proof of arbitrary plugin behavior: it does not infer ownership of heap objects or callbacks. New mutable static/global state and third-party upgrades require ownership review and regression tests.
