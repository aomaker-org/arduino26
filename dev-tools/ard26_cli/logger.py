# file: dev-tools/ard26_cli/logger.py
# Purpose: Operation history and telemetry logger for ard26 CLI invocations
# Target OS: Ubuntu 24.04 / 26.04 LTS (WSL2) + Windows 11 Host

import sys
import time
from pathlib import Path


class OperationLogger:
    """Logs every ard26 CLI invocation and result to agy/log/ard26_history.log."""

    def __init__(self, root_dir: Path):
        self.log_dir = root_dir / "agy" / "log"
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.history_log = self.log_dir / "ard26_history.log"
        self.csv_log = self.log_dir / "ard26_telemetry.csv"
        self._ensure_csv_header()

    def _ensure_csv_header(self):
        if not self.csv_log.exists():
            try:
                with open(self.csv_log, "w", encoding="utf-8") as f:
                    f.write("timestamp,command,sketch,port,status,exit_code\n")
            except Exception:  # noqa: BLE001, S110
                pass

    def log_operation(self, command: str, sketch: str, port: str, status: str, exit_code: int = 0):
        ts = time.strftime("%Y-%m-%d %H:%M:%S")
        cmd_str = f"ard26 {command} {' '.join(sys.argv[2:])}".strip()
        
        # Log to human-readable log file
        log_line = f"[{ts}] CMD: '{cmd_str}' | SKETCH: {sketch} | PORT: {port} | STATUS: {status} (code {exit_code})\n"
        try:
            with open(self.history_log, "a", encoding="utf-8") as f:
                f.write(log_line)
        except Exception as e:  # noqa: BLE001
            print(f"[!] Warning: Could not write history log: {e}", file=sys.stderr)

        # Log to CSV telemetry
        csv_line = f'"{ts}","{cmd_str}","{sketch}","{port}","{status}",{exit_code}\n'
        try:
            with open(self.csv_log, "a", encoding="utf-8") as f:
                f.write(csv_line)
        except Exception:  # noqa: BLE001, S110
            pass

# file dev-tools/ard26_cli/logger.py ends
