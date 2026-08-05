# file: dev-tools/ard26_cli/telemetry.py
# Purpose: Collision-free telemetry logger with custom timestamps, headers, and footers
# Target OS: Ubuntu 24.04 / 26.04 LTS (WSL2) + Windows 11 Host

import sys
import time
from pathlib import Path


class TelemetryLogger:
    """Manages collision-free serial telemetry log files with headers, footers, and relative elapsed time."""

    def __init__(self, root_dir: Path, port: str, baud: int):
        self.root_dir = root_dir
        self.port = port
        self.baud = baud
        self.log_dir = root_dir / "agy" / "log"
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        self.start_time = time.time()
        self.start_struct = time.localtime(self.start_time)
        self.lines_count = 0

        # Collision-free filename generation (timestamp_nnn)
        base_ts = time.strftime("%y%m%d_%H%M%S", self.start_struct)
        seq = 1
        while True:
            candidate = self.log_dir / f"serial_telemetry_{base_ts}_{seq:03d}.log"
            if not candidate.exists():
                self.session_log = candidate
                break
            seq += 1

        self.master_log = self.log_dir / "serial_telemetry.log"
        self._write_header()

    def _write_header(self):
        full_start = time.strftime("%Y-%m-%d %H:%M:%S %Z", self.start_struct)
        header = (
            f"==========================================================\n"
            f"Arduino26 Telemetry Log Started: {full_start}\n"
            f"Target Port : {self.port} | Baud Rate: {self.baud}\n"
            f"Log File    : {self.session_log.name}\n"
            f"==========================================================\n"
        )
        self._append_text(header)

    def log_line(self, line: str) -> str:
        """Formats and writes a serial output line with YYMMDD +HH:MM:SS timestamp."""
        self.lines_count += 1
        elapsed_sec = int(time.time() - self.start_time)
        hours = elapsed_sec // 3600
        minutes = (elapsed_sec % 3600) // 60
        seconds = elapsed_sec % 60
        
        date_prefix = time.strftime("%y%m%d", time.localtime())
        elapsed_prefix = f"+{hours:02d}:{minutes:02d}:{seconds:02d}"
        formatted = f"[{date_prefix} {elapsed_prefix}] {line}"
        
        self._append_text(formatted + "\n")
        return formatted

    def close(self, status: str = "Clean Exit (Ctrl+C)"):
        """Appends session summary footer on exit."""
        end_time = time.time()
        end_struct = time.localtime(end_time)
        full_end = time.strftime("%Y-%m-%d %H:%M:%S %Z", end_struct)
        
        duration_sec = int(end_time - self.start_time)
        dh = duration_sec // 3600
        dm = (duration_sec % 3600) // 60
        ds = duration_sec % 60
        duration_str = f"{dh:02d}:{dm:02d}:{ds:02d}"

        footer = (
            f"==========================================================\n"
            f"Arduino26 Telemetry Log Ended: {full_end}\n"
            f"Status       : {status}\n"
            f"Duration     : {duration_str} | Total Lines: {self.lines_count}\n"
            f"==========================================================\n"
        )
        self._append_text(footer)

    def _append_text(self, text: str):
        """Appends text to both session log and master log without overwriting."""
        try:
            with open(self.session_log, "a", encoding="utf-8") as f:
                f.write(text)
                f.flush()
        except Exception as e:  # noqa: BLE001
            print(f"[!] Warning: Could not write session log: {e}", file=sys.stderr)

        try:
            with open(self.master_log, "a", encoding="utf-8") as f:
                f.write(text)
                f.flush()
        except Exception:  # noqa: BLE001, S110
            pass

# file dev-tools/ard26_cli/telemetry.py ends
