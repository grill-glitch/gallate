#!/usr/bin/env python3
"""
unpack.py — example pre script for a gallate project.

Run before `tool -e`. Unpacks the input archive so that the CLI
sees a directory tree, not a packed file.

This script runs with working directory = Project Root.
"""
import os
import sys
import shutil

input_path = "./game.pfs"
unpacked_dir = "./unpacked"

if not os.path.exists(input_path):
    print(f"error: input not found: {input_path}", file=sys.stderr)
    sys.exit(1)

if os.path.exists(unpacked_dir):
    shutil.rmtree(unpacked_dir)

# Replace this with your real unpack logic. The example just
# creates the directory so the CLI sees *something*.
os.makedirs(unpacked_dir, exist_ok=True)
print(f"unpacked → {unpacked_dir}")
sys.exit(0)