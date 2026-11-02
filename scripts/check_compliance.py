#!/usr/bin/env python3
"""Fail the build if production pages contain banned claims or em dashes."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKIP_DIRS = {"design", "mockups-src", "build", "node_modules", ".git"}
PATTERNS = [
    ("em dash", re.compile(r"—|&mdash;|&#8212;|&#x2014;", re.I)),
    ("10-year workmanship", re.compile(r"10-year workmanship", re.I)),
    ("SAPN Accredited", re.compile(r"SAPN Accredited", re.I)),
    ("CEC accredited", re.compile(r"CEC.accredited", re.I)),
    ("team email", re.compile(r"team@earthedenergy", re.I)),
    ("support email", re.compile(r"support@earthedenergy", re.I)),
]


def scan_file(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8", errors="replace")
    hits = []
    for name, pattern in PATTERNS:
        if pattern.search(text):
            hits.append(name)
    return hits


def main() -> int:
    failures = []
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if path.suffix.lower() not in {".html", ".js", ".css"}:
            continue
        if "scripts" in path.parts:
            continue
        hits = scan_file(path)
        if hits:
            failures.append(f"{path.relative_to(ROOT)}: {', '.join(hits)}")
    if failures:
        print("Compliance check failed:")
        print("\n".join(failures))
        return 1
    print("Compliance check passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
