# file: dev-tools/lint_hygiene.py
# Purpose: Lint text files in the workspace for header, footer and column width rules.
# Target OS: Ubuntu 24.04 / 26.04 LTS (WSL2) + Windows 11 Host

import argparse
import os
import platform
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from ard26_cli.config import Config

# Files/folders to exclude from checks
EXCLUDED_DIRS = {".git", ".venv", ".ruff_cache", "arduino26_tools.egg-info", "target"}
EXCLUDED_FILES = {"LICENSE"}
# Checked file extensions
TEXT_EXTENSIONS = {".md", ".toml", ".txt", ".sh", ".py", ".env", ".ino", ".json"}

def check_file(filepath: Path, root_dir: Path) -> list[str]:
    errors = []
    rel_path = filepath.relative_to(root_dir)
    
    try:
        content = filepath.read_text(encoding="utf-8", errors="ignore")
    except OSError as e:
        return [f"Could not read file: {e}"]
        
    lines = [line for line in content.splitlines()]
    if not lines:
        return []

    # Check 1: Header rule (shebang-aware)
    header_found = False
    expected_header = str(rel_path)
    
    # Check first two lines for path header reference
    for line in lines[:2]:
        if expected_header in line:
            header_found = True
            break
            
    if not header_found:
        errors.append(
            f"Missing or invalid header. "
            f"Expected header referencing: '{expected_header}'"
        )

    # Check 2: Footer rule
    last_non_empty = ""
    for line in reversed(lines):
        if line.strip():
            last_non_empty = line
            break
            
    expected_footer = f"{rel_path} ends"
    if expected_footer not in last_non_empty:
        errors.append(
            f"Missing or invalid footer. "
            f"Expected it to contain '{expected_footer}' but got: '{last_non_empty}'"
        )

    # Check 3: 80 column width rule for text files (.md, .txt)
    if filepath.suffix in {".md", ".txt"}:
        for idx, line in enumerate(lines, 1):
            if len(line) > 80:
                # Bypass tables, links or code snippets exceeding width
                if "|" in line or "http" in line or line.startswith(("    ", "```")):
                    continue
                errors.append(f"Line {idx} exceeds 80 characters ({len(line)} chars): {line[:30]}...")

    return errors

def main():
    parser = argparse.ArgumentParser(description="Workspace Hygiene Linter")
    parser.add_argument("-q", "--quiet", action="store_true", help="Quiet mode. Suppress stdout.")
    args_cli = parser.parse_args()

    # Ingest Config settings
    cfg = Config()
    use_delta = cfg.delta_timestamps

    root_dir = Path(__file__).resolve().parent.parent
    failed = False
    
    # Track logged events with high-precision baseline timing
    start_time_ns = time.time_ns()
    log_events = []
    
    def log_event(message: str):
        delta_ms = (time.time_ns() - start_time_ns) / 1_000_000.0
        log_events.append((delta_ms, message))
        if not args_cli.quiet:
            print(message)

    # Naming scheme: YYMMDD_nnn (e.g. YYMMDD_001)
    yymmdd = datetime.now(timezone.utc).strftime("%y%m%d")
    log_dir = root_dir / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Non-destructive search for collision-free index 'nnn'
    idx = 1
    while True:
        log_file = log_dir / f"hygiene_failures_{yymmdd}_{idx:03d}.log"
        if not log_file.exists():
            break
        idx += 1

    for root, dirs, files in os.walk(root_dir):
        # Exclude directories
        dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS and "target" not in d]
        for file in files:
            if file in EXCLUDED_FILES:
                continue
                
            filepath = Path(root) / file
            if filepath.suffix in TEXT_EXTENSIONS:
                errors = check_file(filepath, root_dir)
                if errors:
                    failed = True
                    log_event(f"[X] {filepath.relative_to(root_dir)}")
                    for err in errors:
                        log_event(f"    - {err}")
                        
    if failed:
        # Construct header metadata
        header_lines = [
            "==========================================================",
            " Workspace Hygiene Log File",
            "==========================================================",
            f"Timestamp    : {datetime.now(timezone.utc).isoformat()}",
            f"OS Platform  : {platform.system()} {platform.release()}",
            f"Python Ver   : {platform.python_version()}",
            f"Workspace    : {root_dir}",
            f"Timing Mode  : {'Relative Delta (+ms)' if use_delta else 'Absolute'}",
            "==========================================================",
            ""
        ]
        
        body_lines = []
        for delta, msg in log_events:
            if use_delta:
                body_lines.append(f"[+{delta:07.2f}ms] {msg}")
            else:
                body_lines.append(f"[{datetime.now(timezone.utc).strftime('%H:%M:%S')}] {msg}")
                
        log_content = "\n".join(header_lines + body_lines) + "\n"
        log_file.write_text(log_content, encoding="utf-8")
        
        if not args_cli.quiet:
            print(f"\n[!] Hygiene validation failed. Log written to: {log_file.relative_to(root_dir)}")
        sys.exit(1)
    else:
        success_msg = f"[SUCCESS] All files pass workspace hygiene checks ({datetime.now(timezone.utc).isoformat()})."
        if not args_cli.quiet:
            print(success_msg)
        sys.exit(0)

if __name__ == "__main__":
    main()

# file dev-tools/lint_hygiene.py ends

