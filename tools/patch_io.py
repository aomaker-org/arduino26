#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ==============================================================================
# Filename:     tools/patch_io.py
# Purpose:      Bridge wrapper for input (clip2files) and output (files2clip)
# Target OS:    Ubuntu 24.04 / 26.04 LTS / WSL2 / Linux Native
# Lineage:      Arduino26 Infrastructure
# Updated:      2026-07-31
# Attribution:  fekerr & Gemini
# ==============================================================================

import sys
import os
import subprocess

def patch_in(file_path):
    print(f"[+] Patching Input: {file_path}")
    script_dir = os.path.dirname(os.path.realpath(__file__))
    tool_path = os.path.join(script_dir, "clip2files")
    if os.path.exists(tool_path):
        cmd = [sys.executable, tool_path]
        subprocess.run(cmd)
    else:
        print(f"[-] Error: clip2files not found at {tool_path}")

def patch_out(file_path):
    print(f"[+] Patching Output: {file_path}")
    script_dir = os.path.dirname(os.path.realpath(__file__))
    tool_path = os.path.join(script_dir, "files2clip")
    if os.path.exists(tool_path):
        cmd = [sys.executable, tool_path, file_path]
        subprocess.run(cmd)
    else:
        print(f"[-] Error: files2clip not found at {tool_path}")

def main():
    if len(sys.argv) < 2:
        print("Usage: patch_io.py [in|out] [path]")
        sys.exit(1)

    mode = sys.argv[1]
    file_path = sys.argv[2] if len(sys.argv) > 2 else "."

    if mode == "in":
        patch_in(file_path)
    elif mode == "out":
        patch_out(file_path)
    else:
        print(f"[-] Unknown mode: {mode}")
        sys.exit(1)

if __name__ == "__main__":
    main()
