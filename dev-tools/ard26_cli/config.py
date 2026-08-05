# file: dev-tools/ard26_cli/config.py
# Purpose: Configuration parser for ard26 CLI reading arduino_config.toml
# Target OS: Ubuntu 24.04 / 26.04 LTS (WSL2) + Windows 11 Host

import os
import sys
from pathlib import Path
from typing import ClassVar

if sys.version_info >= (3, 11):
    import tomllib
else:
    try:
        import tomli as tomllib
    except ImportError:
        tomllib = None


class Config:
    """Manages workspace configuration settings loaded from arduino_config.toml."""
    
    DEFAULT_CONFIG: ClassVar[dict] = {
        "board": {
            "fqbn": "arduino:avr:uno",
            "mcu": "atmega328p"
        },
        "port": {
            "wsl": "/dev/ttyUSB0",
            "win": "COM5",
            "autodetect": True
        },
        "baud": {
            "default": 115200,
            "dht11": 9600,
            "diag": 115200
        },
        "paths": {
            "sketches_dir": "sketches",
            "tools_dir": "tools",
            "dev_tools_dir": "dev-tools"
        }
    }

    def __init__(self, root_dir=None):
        self.root_dir = Path(root_dir or os.environ.get("ARDUINO26_ROOT", os.getcwd()))
        self.config_path = self.root_dir / "arduino_config.toml"
        self.data = self._load_config()

    def _load_config(self):
        config_data = dict(self.DEFAULT_CONFIG)
        if self.config_path.exists() and tomllib is not None:
            try:
                with open(self.config_path, "rb") as f:
                    loaded = tomllib.load(f)
                    # Deep update dictionary
                    for section, values in loaded.items():
                        if section in config_data and isinstance(values, dict):
                            config_data[section].update(values)
                        else:
                            config_data[section] = values
            except Exception as e:  # noqa: BLE001
                print(f"[!] Warning: Could not parse {self.config_path}: {e}", file=sys.stderr)
        return config_data

    @property
    def fqbn(self) -> str:
        return self.data.get("board", {}).get("fqbn", "arduino:avr:uno")

    @property
    def port_wsl(self) -> str:
        return self.data.get("port", {}).get("wsl", "/dev/ttyUSB0")

    @property
    def port_win(self) -> str:
        return self.data.get("port", {}).get("win", "COM5")

    @property
    def autodetect(self) -> bool:
        return self.data.get("port", {}).get("autodetect", True)

    @property
    def baud_default(self) -> int:
        return self.data.get("baud", {}).get("default", 115200)

    @property
    def last_compiled_sketch(self) -> str:
        return self.data.get("state", {}).get("last_compiled_sketch", "uno_blink")

    @property
    def active_method(self) -> str:
        return self.data.get("state", {}).get("active_method", "wsl")

    @property
    def preferred_port(self) -> str:
        return self.data.get("state", {}).get("preferred_port", "")

    def set_last_compiled_sketch(self, sketch_name: str):
        if "state" not in self.data:
            self.data["state"] = {}
        self.data["state"]["last_compiled_sketch"] = sketch_name
        self._write_config()

    def save_successful_upload(self, port: str, method: str):
        """Saves working port and upload method as defaults for future invocations."""
        if "state" not in self.data:
            self.data["state"] = {}
        self.data["state"]["active_method"] = method
        self.data["state"]["preferred_port"] = port
        self._write_config()

    def _write_config(self):
        """Persists updated state back to arduino_config.toml."""
        try:
            lines = [
                "# file: arduino_config.toml",
                "# Purpose: Visible, non-hidden TOML configuration file for the ard26 CLI tool",
                "# Target OS: Ubuntu 24.04 / 26.04 LTS (WSL2) + Windows 11 Host",
                "",
                "[board]",
                f'fqbn = "{self.fqbn}"',
                f'mcu = "{self.data.get("board", {}).get("mcu", "atmega328p")}"',
                "",
                "[port]",
                f'wsl = "{self.port_wsl}"',
                f'win = "{self.port_win}"',
                f'autodetect = {str(self.autodetect).lower()}',
                "",
                "[baud]",
                f'default = {self.baud_default}',
                f'dht11 = {self.data.get("baud", {}).get("dht11", 9600)}',
                f'diag = {self.data.get("baud", {}).get("diag", 115200)}',
                "",
                "[paths]",
                f'sketches_dir = "{self.data.get("paths", {}).get("sketches_dir", "sketches")}"',
                f'tools_dir = "{self.data.get("paths", {}).get("tools_dir", "tools")}"',
                f'dev_tools_dir = "{self.data.get("paths", {}).get("dev_tools_dir", "dev-tools")}"',
                "",
                "[state]",
                f'last_compiled_sketch = "{self.last_compiled_sketch}"',
                f'active_method = "{self.active_method}"',
                f'preferred_port = "{self.preferred_port}"',
                "",
                "# file arduino_config.toml ends",
                ""
            ]
            with open(self.config_path, "w", encoding="utf-8") as f:
                f.write("\n".join(lines))
        except Exception as e:  # noqa: BLE001
            print(f"[!] Warning: Could not update {self.config_path}: {e}", file=sys.stderr)

# file dev-tools/ard26_cli/config.py ends
