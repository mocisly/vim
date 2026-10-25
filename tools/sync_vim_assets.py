#!/usr/bin/env python3
"""Sync Vim's runtime assets without recopying them at every configure."""

import argparse
import hashlib
import os
from pathlib import Path
import shutil


ASSETS = ("runtime", "ctags58", ".vim", "_vimrc")


def asset_source(source: Path, extras: Path, name: str) -> Path:
    return source / name if name == "runtime" else extras / name


def entries(source: Path, extras: Path):
    for name in ASSETS:
        asset = asset_source(source, extras, name)
        if asset.is_file():
            yield asset, Path(name)
        elif asset.is_dir():
            for directory, folders, files in os.walk(asset):
                folders.sort()
                for filename in sorted(files):
                    path = Path(directory) / filename
                    yield path, Path(name) / path.relative_to(asset)
        elif name == "runtime":
            raise FileNotFoundError(asset)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--extras", type=Path, required=True)
    parser.add_argument("--build-root", type=Path, required=True)
    parser.add_argument("--configuration", choices=("Debug", "Release"), required=True)
    args = parser.parse_args()
    source = args.source.resolve()
    extras = args.extras.resolve()
    build_root = args.build_root.resolve()
    destination = build_root / args.configuration / "vim"
    if (source != build_root / "vim-source" or destination.resolve() != destination
            or extras != build_root.parent.parent / "assets/vim"):
        parser.error("Unexpected Vim source or destination path")

    digest = hashlib.sha256()
    stale = False
    for name in ASSETS:
        asset = asset_source(source, extras, name)
        if not asset.exists():
            digest.update(f"{name}:absent\n".encode())
            if (destination / name).exists():
                stale = True
    for path, relative in entries(source, extras):
        source_stat = path.stat()
        digest.update(
            f"{relative.as_posix()}\0{source_stat.st_size}\0{source_stat.st_mtime_ns}\n".encode()
        )
        installed = destination / relative
        if not installed.is_file():
            stale = True
        elif not stale:
            installed_stat = installed.stat()
            if (installed_stat.st_size, installed_stat.st_mtime_ns) != (
                source_stat.st_size, source_stat.st_mtime_ns
            ):
                stale = True

    expected = digest.hexdigest()
    stamp = destination / ".vim-assets-signature"
    if not stale and stamp.is_file() and stamp.read_text() == expected:
        print(f"Vim {args.configuration} runtime files are current")
        return
    if stamp.is_file() and stamp.read_text() != expected:
        # Files removed by an upstream update must also disappear from the
        # deployed runtime, even when every remaining file still matches.
        stale = True
    if not stale:
        destination.mkdir(parents=True, exist_ok=True)
        stamp.write_text(expected)
        print(f"Verified Vim {args.configuration} runtime files")
        return

    destination.mkdir(parents=True, exist_ok=True)
    for name in ASSETS:
        asset = asset_source(source, extras, name)
        installed = destination / name
        if installed.is_dir():
            shutil.rmtree(installed)
        elif installed.exists():
            installed.unlink()
        if not asset.exists():
            continue
        if asset.is_dir():
            shutil.copytree(asset, installed)
        else:
            shutil.copy2(asset, installed)
    stamp.write_text(expected)
    print(f"Synced Vim {args.configuration} runtime files")


if __name__ == "__main__":
    main()
