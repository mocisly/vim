#!/usr/bin/env python3
"""List Vim-owned mutable-storage candidates in a MSVC COFF object set.

The default input is the Debug objects of the VS/Qt ``vim_shared_core`` target.
This is a read-only audit: it runs llvm-readobj and writes only to stdout.

Examples (from the repository root):

    python tools/audit_instance_state.py --summary-only
    python tools/audit_instance_state.py --source buffer.c --source window.c
    python tools/audit_instance_state.py build/vs2026-qt/vim-build/vim_shared_core.dir/Release --json

The report identifies named symbols defined in writable .data/.bss sections
and COFF COMMON declarations (undefined section with a nonzero allocation size).
It does not prove that a symbol is mutated, or that an instance is isolated.
"""

from __future__ import annotations

import argparse
from collections import defaultdict
from dataclasses import asdict, dataclass
from fnmatch import fnmatchcase
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OBJECTS = ROOT / "build/vs2026-qt/vim-build/vim_shared_core.dir/Debug"
FIELD = re.compile(r"^    ([A-Za-z][A-Za-z0-9]*): (.*)$")
SECTION_NUMBER = re.compile(r"\((-?\d+)\)$")


@dataclass(frozen=True)
class Candidate:
    source: str
    object: str
    name: str
    section: str
    scope: str
    offset: int | None
    size: int | None


def source_index() -> dict[str, list[str]]:
    """Map object stems to repository source files, excluding other libraries."""
    index: dict[str, list[str]] = defaultdict(list)
    src = ROOT / "build/vs2026-qt/vim-source/src"
    # The shared target uses Vim's src/, generated pathdef.c, and our runtime
    # entry point. Recursive indexing would include duplicate libvterm names.
    for directory in (src, src / "auto", ROOT / "src/runtime"):
        for source in directory.iterdir():
            if source.is_file() and source.suffix.lower() in {".c", ".cc", ".cpp", ".cxx"}:
                index[source.stem.lower()].append(source.relative_to(ROOT).as_posix())
    return index


def source_for_object(path: Path, index: dict[str, list[str]]) -> str | None:
    matches = index.get(path.stem.lower(), [])
    # A stem shared by several source files cannot be attributed reliably.
    return matches[0] if len(matches) == 1 else None


def read_coff(path: Path, readobj: str) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    result = subprocess.run(
        [readobj, "--sections", "--symbols", str(path)],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    if result.returncode:
        raise RuntimeError(f"{path}: llvm-readobj failed: {result.stderr.strip()}")
    if "Format: COFF-" not in result.stdout:
        raise RuntimeError(f"{path}: expected a COFF object")

    sections: list[dict[str, str]] = []
    symbols: list[dict[str, str]] = []
    current: dict[str, str] | None = None
    destination: list[dict[str, str]] | None = None
    for line in result.stdout.splitlines():
        if line == "  Section {":
            current, destination = {}, sections
        elif line == "  Symbol {":
            current, destination = {}, symbols
        elif line == "  }" and current is not None:
            assert destination is not None
            destination.append(current)
            current, destination = None, None
        elif current is not None:
            match = FIELD.match(line)
            if match:
                current[match.group(1)] = match.group(2)
            elif "IMAGE_SCN_MEM_WRITE" in line:
                current["Writable"] = "true"
    return sections, symbols


def section_kind(name: str) -> str | None:
    if name in {".data", ".bss"} or name.startswith((".data$", ".bss$")):
        return "ordinary"
    if name == ".tls" or name.startswith(".tls$"):
        return "tls"
    return None


def compiler_generated(name: str) -> bool:
    # MSVC emits writable-section string literals and numeric constants with
    # these synthetic names. Keep all ordinary named Vim variables, including
    # decorated names for function-local static variables.
    return name.startswith((
        "$", "??_C@", "??_R0", "__real@", "__xmm@",  # literals / C++ RTTI
        "?_OptionsStorage@?1??__local_stdio_",  # MSVC CRT inline helper
    )) or name == "_Avx2WmemEnabledWeakValue"  # MSVC runtime helper


def find_candidates(
    path: Path, source: str, readobj: str
) -> tuple[list[Candidate], int, int]:
    section_records, symbols = read_coff(path, readobj)
    sections: dict[int, tuple[str, bool]] = {}
    for record in section_records:
        if "Number" in record and "Name" in record:
            number = int(record["Number"], 0)
            name = record["Name"].split(" (", 1)[0]
            sections[number] = (name, record.get("Writable") == "true")

    candidates: list[Candidate] = []
    tls_count = 0
    synthetic_count = 0
    for symbol in symbols:
        section_ref = symbol.get("Section", "")
        storage = symbol.get("StorageClass", "")
        if not storage.startswith(("Static ", "External ")):
            continue
        if symbol.get("ComplexType", "").startswith("Function "):
            continue
        name = symbol.get("Name", "")
        if not name:
            continue
        value = int(symbol.get("Value", "0"), 0)
        if section_ref == "IMAGE_SYM_UNDEFINED (0)":
            # COFF COMMON symbols are tentative data definitions.  Their
            # Value is a byte size, unlike a true unresolved import (Value 0).
            if storage.startswith("External ") and value > 0:
                if compiler_generated(name):
                    synthetic_count += 1
                    continue
                candidates.append(Candidate(
                    source=source,
                    object=path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else str(path),
                    name=name,
                    section="COMMON",
                    scope="global",
                    offset=None,
                    size=value,
                ))
            continue
        match = SECTION_NUMBER.search(section_ref)
        if match is None:
            continue
        section = sections.get(int(match.group(1)))
        if section is None:
            continue  # absolute or a missing section
        section_name, writable = section
        kind = section_kind(section_name)
        if kind is None or not writable:
            continue
        if name == section_name and symbol.get("AuxSymbolCount") != "0":
            continue
        if compiler_generated(name):
            synthetic_count += 1
            continue
        if kind == "tls":
            tls_count += 1
            continue
        candidates.append(
            Candidate(
                source=source,
                object=path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else str(path),
                name=name,
                section=section_name,
                scope="static" if storage.startswith("Static ") else "global",
                offset=value,
                size=None,
            )
        )
    return candidates, tls_count, synthetic_count


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        "objects",
        nargs="*",
        type=Path,
        help=f".obj files or directories (default: {DEFAULT_OBJECTS.relative_to(ROOT)})",
    )
    parser.add_argument("--readobj", default=shutil.which("llvm-readobj"), help="path to llvm-readobj")
    parser.add_argument(
        "--source",
        action="append",
        metavar="GLOB",
        help="include matching source paths or file names (repeatable, e.g. buffer.c)",
    )
    parser.add_argument("--summary-only", action="store_true", help="show per-source counts without symbol lines")
    parser.add_argument("--json", action="store_true", help="print machine-readable report to stdout")
    args = parser.parse_args()

    if not args.readobj:
        parser.error("llvm-readobj was not found; set --readobj to its executable path")
    inputs = args.objects or [DEFAULT_OBJECTS]
    object_files: set[Path] = set()
    for item in inputs:
        path = item.resolve()
        if path.is_file() and path.suffix.lower() == ".obj":
            object_files.add(path)
        elif path.is_dir():
            object_files.update(path.rglob("*.obj"))
        else:
            parser.error(f"not an .obj file or directory: {item}")
    if not object_files:
        parser.error("no .obj files found; build vim_shared_core or pass an object directory")

    sources = source_index()
    selected: list[tuple[Path, str]] = []
    skipped_objects: list[str] = []
    stale_objects: list[str] = []
    for path in sorted(object_files):
        source = source_for_object(path, sources)
        if source is None:
            skipped_objects.append(str(path))
            continue
        if args.source and not any(
            fnmatchcase(source.lower(), pattern.lower())
            or fnmatchcase(Path(source).name.lower(), pattern.lower())
            for pattern in args.source
        ):
            continue
        selected.append((path, source))
        if (ROOT / source).stat().st_mtime_ns > path.stat().st_mtime_ns:
            stale_objects.append(source)
    if not selected:
        parser.error("no .obj files matched Vim sources and the --source filters")

    by_source: dict[str, list[Candidate]] = defaultdict(list)
    tls_total = synthetic_total = 0
    for path, source in selected:
        try:
            candidates, tls_count, synthetic_count = find_candidates(path, source, args.readobj)
        except (OSError, RuntimeError, ValueError) as error:
            parser.error(str(error))
        by_source[source].extend(candidates)
        tls_total += tls_count
        synthetic_total += synthetic_count

    ordered = sorted(by_source, key=lambda source: (-len(by_source[source]), source))
    total = sum(len(candidates) for candidates in by_source.values())
    if args.json:
        print(json.dumps({
            "objects_scanned": len(selected),
            "objects_without_unique_vim_source": skipped_objects,
            "objects_older_than_source": stale_objects,
            "ordinary_symbol_count": total,
            "tls_symbol_count": tls_total,
            "compiler_generated_omitted": synthetic_total,
            "sources": [
                {"source": source, "count": len(by_source[source]),
                 "symbols": [asdict(item) for item in sorted(by_source[source], key=lambda item: (item.section, item.name, item.offset or 0))]}
                for source in ordered
            ],
        }, indent=2))
        return 0

    print(f"Scanned {len(selected)} Vim source objects; {total} ordinary writable/COMMON symbols "
          f"in {sum(bool(by_source[source]) for source in ordered)} source files.")
    print(f"TLS symbols: {tls_total}; compiler-generated names omitted: {synthetic_total}; "
          f"objects without a unique Vim source: {len(skipped_objects)}; "
          f"objects older than source: {len(stale_objects)}.")
    if skipped_objects:
        print("Unmapped objects: " + ", ".join(skipped_objects))
    if stale_objects:
        print("Older than source: " + ", ".join(stale_objects))
    for source in ordered:
        candidates = by_source[source]
        if not candidates:
            continue
        if not args.summary_only:
            print()
        print(f"{source}: {len(candidates)}")
        if not args.summary_only:
            for item in sorted(candidates, key=lambda item: (item.section, item.name, item.offset or 0)):
                detail = f" (size={item.size})" if item.size is not None else ""
                print(f"  {item.section:<12} {item.scope:<6} {item.name}{detail}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
