#!/usr/bin/env python3
"""
repack.py — example post script for a gallate project.

Run after `tool -i`. Repacks the unpacked directory back into the
output archive.

This script runs with working directory = Project Root.
"""
import os
import sys

output_path = "./game-zh.pfs"
unpacked_dir = "./unpacked"

if not os.path.exists(unpacked_dir):
    print(f"error: unpacked dir missing: {unpacked_dir}", file=sys.stderr)
    sys.exit(1)

# Replace this with your real repack logic. The example just
# writes a marker file so you can see the script ran.
with open(output_path, "wb") as f:
    f.write(b"GALLATE-OUTPUT\n")

print(f"repacked → {output_path}")
sys.exit(0)