# file: dev-tools/ard26_cli/config.py
# Purpose: Configuration parser for ard26 CLI reading arduino_config.toml
# Target OS: Ubuntu 24.04 / 26.04 LTS (WSL2) + Windows 11 Host

import os
import sys
from pathlib import Path

if sys.version_info >= (3, 11):
    import tomllib
else:
    try:
        import tomli as tomllib
    except ImportError:
        tomllib = None


class Config:
    """Manages workspace configuration settings loaded from arduino_config.toml."""
    
    DEFAULT_CONFIG = {
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
            except Exception as e:
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

# file dev-tools/ard26_cli/config.py ends
