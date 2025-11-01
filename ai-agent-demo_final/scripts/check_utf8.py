#!/usr/bin/env python3
"""Check that all .py files under app/ are valid UTF-8.
Exit with non-zero status if any file is not UTF-8 decodable.
"""
from pathlib import Path
import sys

root = Path(__file__).resolve().parents[1]
app_dir = root / "app"

failed = []
for p in app_dir.rglob("*.py"):
    try:
        p.read_bytes().decode("utf-8")
    except Exception:
        failed.append(str(p))

if failed:
    print("The following files are not valid UTF-8:\n")
    for f in failed:
        print(f" - {f}")
    sys.exit(2)
else:
    print("All .py files under app/ are valid UTF-8.")
    sys.exit(0)
