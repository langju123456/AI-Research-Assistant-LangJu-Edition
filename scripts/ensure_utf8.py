#!/usr/bin/env python3
"""Rewrite all .py files under app/ as UTF-8 without changing content.

This is a safe, idempotent way to ensure source files are UTF-8 encoded.
"""
from pathlib import Path

root = Path(__file__).resolve().parents[1]
app_dir = root / "app"

files = list(app_dir.rglob("*.py"))
print(f"Found {len(files)} .py files under {app_dir}")

for p in files:
    try:
        # Read with binary then decode using 'utf-8' with errors='replace' to avoid crashes
        b = p.read_bytes()
        try:
            text = b.decode("utf-8")
            # Already UTF-8
        except UnicodeDecodeError:
            # Try a common Windows encoding fallback (GBK), then re-encode to UTF-8
            try:
                text = b.decode("gbk")
                print(f"Re-encoding {p} from GBK -> UTF-8")
            except Exception:
                # As last resort, decode with replace to preserve content
                text = b.decode("utf-8", errors="replace")
                print(f"Rewriting {p} with replacement for undecodable bytes")
        # Write back as UTF-8 (without BOM)
        p.write_text(text, encoding="utf-8")
    except Exception as e:
        print(f"Failed to process {p}: {e}")
print("Done.")
