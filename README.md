# Vim runtime integration

This project builds two independent Vim instance handles in one Windows DLL,
with a C++/Qt host. Vim's upstream sources and the integration are kept in
separate directories:

```text
upstream/vim/       Vim source tree (unchanged)
patches/vim/        Required changes to Vim source and CMake hooks
cmake/              Integration CMake modules
include/            Public C API
src/runtime/        DLL entry point and private instance declarations
src/qt_host/        Qt host
tests/              Dual-instance regression suite
tools/              Source preparation and state audit tools
assets/vim/         Optional local .vim, ctags58, and _vimrc assets
build/              Generated patched Vim tree and build products
```

The current Vim base is Git commit `c13ee0183744503bb522b550d3878bb99afcb7c3`.
The source preparation step copies `upstream/vim` into `build/vs2026-qt/vim-source`
and applies patches there. It never patches `upstream/vim` in place. The
generated copy and deployed runtime files are refreshed when their inputs
change.

## Build and test

```powershell
cmake --preset vs2026-qt
cmake --build build/vs2026-qt --config Debug --target vim_qt_host vim --parallel 8
python tests/test_runtime.py --configuration Debug
```

The same commands work with `Release`. The build requires the Visual Studio,
CMake, Python, and Qt versions specified in `CMakePresets.json` and
`cmake/VimQtHost.cmake`. Local files in `assets/vim` are copied beside the
binaries when present; they are ignored by Git.

## Update Vim

Replace only `upstream/vim` with the desired upstream snapshot. Then configure
again. Source preparation will report which patch no longer applies. Adjust
the affected file in `patches/vim`, configure again, and run both Debug and
Release regression suites. Keep integration code, tests, and local assets
outside the upstream tree.

See `docs/dual-instance-runtime.md` for the handle API and its isolation
boundary.
