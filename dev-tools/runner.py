#!/usr/bin/env python3
# file: dev-tools/runner.py
# -*- coding: utf-8 -*-
# ==============================================================================
# Purpose:      Universal process execution wrapper with dual logging, noise
#               throttling (full, filtered, summary), and exit code preservation.
# Type:         Executable / Process Execution Engine
# Rationale:    Ensures zero silent output suppression in log files while providing
#               noise control for CLI/batch.
# Target OS:    Ubuntu 24.04 / 26.04 LTS (WSL2 / Linux Native)
# ==============================================================================
import os
import re
import sys
import time
import argparse
import subprocess
from datetime import datetime
from pathlib import Path

# Patterns considered "noise" in batch / filtered mode (e.g., rclone 5s stats ticks)
NOISE_PATTERNS = [
    re.compile(r"^\s*Transferred:\s+.*", re.IGNORECASE),
    re.compile(r"^\s*Checks:\s+.*", re.IGNORECASE),
    re.compile(r"^\s*Elapsed time:\s+.*", re.IGNORECASE),
    re.compile(r"^\s*Transferring:\s+.*", re.IGNORECASE),
    re.compile(r"^\s*\*\s+.*:\s+\d+%\s+/.*", re.IGNORECASE),
]

# Patterns considered important milestones (always shown even in summary mode)
IMPORTANT_PATTERNS = [
    re.compile(r"^\s*\[[\*\+\!\]]"),  # [*], [+], [!]
    re.compile(r"^\s*==+"),            # =====
    re.compile(r"^\s*--+"),            # -----
    re.compile(r".*error.*", re.IGNORECASE),
    re.compile(r".*failed.*", re.IGNORECASE),
    re.compile(r".*warning.*", re.IGNORECASE),
    re.compile(r".*exception.*", re.IGNORECASE),
]

def is_noise(line: str) -> bool:
    """Return True if line matches known progress tick noise patterns."""
    return any(pattern.match(line) for pattern in NOISE_PATTERNS)

def is_important(line: str) -> bool:
    """Return True if line matches key milestones, headers, or warnings."""
    return any(pattern.match(line) for pattern in IMPORTANT_PATTERNS)

def run_wrapped_command(cmd: list[str], tag: str, mode: str, log_dir: Path) -> int:
    """Runs cmd, tees output to a timestamped log file, and applies noise filtering to stdout."""
    log_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_dir / f"{tag}_{timestamp}.log"
    latest_link = log_dir / f"latest_{tag}.log"

    header = (
        f"==================================================================\n"
        f" RUNNER LOG TRACE: {tag}\n"
        f" Timestamp : {datetime.now().isoformat()}\n"
        f" Command   : {' '.join(cmd)}\n"
        f" Directory : {os.getcwd()}\n"
        f" Noise Mode: {mode}\n"
        f"==================================================================\n\n"
    )

    print(f"\033[1;36m[*] Runner executing [{tag}] in '{mode}' mode...\033[0m")
    print(f"\033[1;34m[*] Logging to: {log_file}\033[0m")

    start_time = time.time()
    exit_code = 1

    try:
        with open(log_file, "w", encoding="utf-8") as lf:
            lf.write(header)
            lf.flush()

            # Update symlink/pointer to latest log immediately at startup
            try:
                if latest_link.is_symlink() or latest_link.exists():
                    latest_link.unlink()
                latest_link.symlink_to(log_file.name)
            except Exception:
                pass

            # Execute command with stderr merged into stdout
            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )

            if proc.stdout:
                for line in proc.stdout:
                    # Always write full un-truncated line to log file
                    lf.write(line)
                    lf.flush()

                    # Apply noise filtering for console output
                    clean_line = line.rstrip("\r\n")
                    if mode == "full":
                        sys.stdout.write(line)
                        sys.stdout.flush()
                    elif mode == "filtered":
                        if not is_noise(clean_line):
                            sys.stdout.write(line)
                            sys.stdout.flush()
                    elif mode == "summary":
                        if is_important(clean_line):
                            sys.stdout.write(line)
                            sys.stdout.flush()
                    elif mode == "quiet":
                        # Quiet mode: suppressed from stdout entirely; preserved in log file
                        pass

            proc.wait()
            exit_code = proc.returncode

            duration = time.time() - start_time
            footer = (
                f"\n==================================================================\n"
                f" RUNNER COMMAND COMPLETED\n"
                f" Exit Code : {exit_code}\n"
                f" Duration  : {duration:.2f} seconds\n"
                f"==================================================================\n"
            )
            lf.write(footer)
            lf.flush()

        # Update symlink/pointer to latest log
        try:
            if latest_link.is_symlink() or latest_link.exists():
                latest_link.unlink()
            latest_link.symlink_to(log_file.name)
        except Exception:
            pass

    except Exception as e:
        print(f"\033[1;31m[!] Runner encountered exception: {e}\033[0m", file=sys.stderr)
        return 1

    if exit_code == 0:
        print(f"\033[1;32m[+] [{tag}] finished successfully (Exit Code 0).\033[0m")
    else:
        print(f"\033[1;31m[!] [{tag}] failed with Exit Code {exit_code}. See log: {log_file}\033[0m")

    return exit_code

def main():
    parser = argparse.ArgumentParser(
        description="Universal process execution wrapper with dual logging and noise throttling.",
        usage="python3 dev-tools/runner.py --tag <TAG> [--mode full|filtered|summary|quiet] -- <COMMAND...>"
    )
    parser.add_argument("--tag", "-t", type=str, default="task", help="Tag identifier for log file naming.")
    parser.add_argument(
        "--mode", "-m",
        type=str,
        choices=["full", "filtered", "summary", "quiet"],
        default=os.environ.get("RUNNER_MODE", "full"),
        help="Console noise control mode (default: full, or via RUNNER_MODE env var)."
    )
    parser.add_argument("--log-dir", type=str, default="logs", help="Directory path for log output.")
    parser.add_argument("cmd", nargs=argparse.REMAINDER, help="Command and arguments to execute.")

    args = parser.parse_args()

    # Handle '--' separator if passed
    cmd = args.cmd
    if cmd and cmd[0] == "--":
        cmd = cmd[1:]

    if not cmd:
        parser.print_help()
        sys.exit(1)

    log_path = Path(args.log_dir)
    exit_code = run_wrapped_command(cmd, tag=args.tag, mode=args.mode, log_dir=log_path)
    sys.exit(exit_code)

if __name__ == "__main__":
    main()

# file dev-tools/runner.py ends
