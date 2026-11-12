#!/usr/bin/env python3
"""cutest-picture-01 entry: write the picture to /output/entry.png.

The artwork lives in the repository as entry.png, beside this file. This
program copies it to the output location byte for byte, unchanged, so the
judge sees exactly the submitted bytes. Standard library only, no network,
no randomness, no wall-clock dependence: every run writes identical bytes.

Output location, in order of preference:
  1. MAKEFUN_OUTPUT_DIR (a directory; the file is written inside it as
     entry.png), falling back to /output.
  2. MAKEFUN_OUTPUT (a legacy spelling: a full file path), used only when
     MAKEFUN_OUTPUT_DIR is unset.

The program resolves the source image relative to its own location, never
relative to the working directory, so it works from any cwd. If the source
image is missing it exits non-zero with a clear message and writes nothing.
"""

import os
import shutil
import sys
from pathlib import Path

SOURCE_NAME = "entry.png"
DEFAULT_OUTPUT_DIR = "/output"
MAX_BYTES = 1_048_576


def resolve_output_path() -> Path:
    """Return the full path the picture must be written to.

    Blank or whitespace-only environment values are treated as unset, so a
    stray empty variable can never redirect the output to a nonsense path.
    """
    output_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "").strip()
    if output_dir:
        return Path(output_dir) / SOURCE_NAME
    legacy = os.environ.get("MAKEFUN_OUTPUT", "").strip()
    if legacy:
        legacy_path = Path(legacy)
        if legacy_path.is_dir():
            raise ValueError(
                f"MAKEFUN_OUTPUT names a directory, not a file: {legacy}")
        return legacy_path
    return Path(DEFAULT_OUTPUT_DIR) / SOURCE_NAME


def main() -> int:
    source = Path(__file__).resolve().parent / SOURCE_NAME
    if not source.is_file():
        print(f"error: source image not found: {source}", file=sys.stderr)
        return 1

    source_size = source.stat().st_size
    if source_size > MAX_BYTES:
        print(f"error: source image is {source_size} bytes, over the "
              f"{MAX_BYTES}-byte cap; refusing to write an invalid entry",
              file=sys.stderr)
        return 1

    try:
        destination = resolve_output_path()
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    try:
        destination.parent.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        print(f"error: cannot create output directory "
              f"{destination.parent}: {exc}", file=sys.stderr)
        return 1

    try:
        shutil.copyfile(source, destination)
    except OSError as exc:
        print(f"error: cannot write {destination}: {exc}", file=sys.stderr)
        return 1

    if destination.stat().st_size != source_size:
        print(f"error: wrote a partial copy to {destination} "
              f"({destination.stat().st_size} of {source_size} bytes); "
              f"removing it", file=sys.stderr)
        destination.unlink(missing_ok=True)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
