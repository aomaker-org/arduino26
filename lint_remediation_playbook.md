<!-- file: lint_remediation_playbook.md -->
# Lint Remediation Playbook

This playbook lists all the lint issues in the repository and provides a framework for tracking their resolution.

## Options Key
- `[ ]` - Unresolved / Pending
- `[+]` - Fixed manually
- `[A]` - Automatically fixed via `make lint-fix` (ruff check --fix)
- `[W]` - Won't Fix (intentional ignore / noqa / config override)

## Issues Checklist

[A] 1: dev-tools/ard26_cli/cli.py:5:1 - I001: Import block is un-sorted or un-formatted
[A] 2: dev-tools/ard26_cli/cli.py:25:27 - UP045: Use `X | None` for type annotations
[+] 3: dev-tools/ard26_cli/cli.py:84:15 - PLW1510: `subprocess.run` without explicit `check` argument
[+] 4: dev-tools/ard26_cli/cli.py:110:11 - PLW1510: `subprocess.run` without explicit `check` argument
[+] 5: dev-tools/ard26_cli/cli.py:156:17 - PLW1510: `subprocess.run` without explicit `check` argument
[+] 6: dev-tools/ard26_cli/cli.py:172:13 - PLW1510: `subprocess.run` without explicit `check` argument
[+] 7: dev-tools/ard26_cli/cli.py:180:17 - PLW1510: `subprocess.run` without explicit `check` argument
[+] 8: dev-tools/ard26_cli/cli.py:194:19 - PLW1510: `subprocess.run` without explicit `check` argument
[+] 9: dev-tools/ard26_cli/cli.py:197:5 - S110: `try`-`except`-`pass` detected, consider logging the exception
[+] 10: dev-tools/ard26_cli/cli.py:197:12 - BLE001: Do not catch blind exception: `Exception`
[+] 11: dev-tools/ard26_cli/cli.py:207:15 - UP022: Prefer `capture_output` over sending `stdout` and `stderr` to `PIPE`
[+] 12: dev-tools/ard26_cli/cli.py:207:15 - PLW1510: `subprocess.run` without explicit `check` argument
[A] 13: dev-tools/ard26_cli/cli.py:216:23 - F541: f-string without any placeholders
[A] 14: dev-tools/ard26_cli/cli.py:217:23 - F541: f-string without any placeholders
[A] 15: dev-tools/ard26_cli/cli.py:218:23 - F541: f-string without any placeholders
[A] 16: dev-tools/ard26_cli/cli.py:219:23 - F541: f-string without any placeholders
[A] 17: dev-tools/ard26_cli/cli.py:220:23 - F541: f-string without any placeholders
[A] 18: dev-tools/ard26_cli/cli.py:221:23 - F541: f-string without any placeholders
[A] 19: dev-tools/ard26_cli/cli.py:222:23 - F541: f-string without any placeholders
[A] 20: dev-tools/ard26_cli/cli.py:223:23 - F541: f-string without any placeholders
[A] 21: dev-tools/ard26_cli/cli.py:224:23 - F541: f-string without any placeholders
[A] 22: dev-tools/ard26_cli/cli.py:225:23 - F541: f-string without any placeholders
[A] 23: dev-tools/ard26_cli/cli.py:226:23 - F541: f-string without any placeholders
[+] 24: dev-tools/ard26_cli/cli.py:237:11 - PLW1510: `subprocess.run` without explicit `check` argument
[A] 25: dev-tools/ard26_cli/cli.py:251:19 - F541: f-string without any placeholders
[A] 26: dev-tools/ard26_cli/cli.py:253:19 - F541: f-string without any placeholders
[A] 27: dev-tools/ard26_cli/cli.py:255:19 - F541: f-string without any placeholders
[A] 28: dev-tools/ard26_cli/cli.py:300:11 - F541: f-string without any placeholders
[A] 29: dev-tools/ard26_cli/cli.py:301:11 - F541: f-string without any placeholders
[A] 30: dev-tools/ard26_cli/cli.py:302:11 - F541: f-string without any placeholders
[A] 31: dev-tools/ard26_cli/cli.py:306:11 - F541: f-string without any placeholders
[A] 32: dev-tools/ard26_cli/cli.py:308:11 - F541: f-string without any placeholders
[A] 33: dev-tools/ard26_cli/cli.py:309:11 - F541: f-string without any placeholders
[+] 34: dev-tools/ard26_cli/cli.py:319:9 - PLW1510: `subprocess.run` without explicit `check` argument
[+] 35: dev-tools/ard26_cli/cli.py:341:12 - BLE001: Do not catch blind exception: `Exception`
[+] 36: dev-tools/ard26_cli/cli.py:423:13 - S110: `try`-`except`-`pass` detected, consider logging the exception
[+] 37: dev-tools/ard26_cli/cli.py:423:20 - BLE001: Do not catch blind exception: `Exception`
[+] 38: dev-tools/ard26_cli/cli.py:441:17 - S110: `try`-`except`-`pass` detected, consider logging the exception
[+] 39: dev-tools/ard26_cli/cli.py:441:24 - BLE001: Do not catch blind exception: `Exception`
[+] 40: dev-tools/ard26_cli/config.py:21:22 - RUF012: Mutable default value for class attribute
[+] 41: dev-tools/ard26_cli/config.py:60:20 - BLE001: Do not catch blind exception: `Exception`
[+] 42: dev-tools/ard26_cli/config.py:147:16 - BLE001: Do not catch blind exception: `Exception`
[A] 43: dev-tools/ard26_cli/detector.py:5:1 - I001: Import block is un-sorted or un-formatted
[+] 44: dev-tools/ard26_cli/detector.py:11:1 - UP035: `typing.List` is deprecated, use `list` instead
[+] 45: dev-tools/ard26_cli/detector.py:11:1 - UP035: `typing.Dict` is deprecated, use `dict` instead
[A] 46: dev-tools/ard26_cli/detector.py:23:28 - UP045: Use `X | None` for type annotations
[+] 47: dev-tools/ard26_cli/detector.py:38:31 - UP006: Use `list` instead of `List` for type annotation
[+] 48: dev-tools/ard26_cli/detector.py:38:36 - UP006: Use `dict` instead of `Dict` for type annotation
[+] 49: dev-tools/ard26_cli/detector.py:46:19 - UP022: Prefer `capture_output` over sending `stdout` and `stderr` to `PIPE`
[+] 50: dev-tools/ard26_cli/detector.py:46:19 - PLW1510: `subprocess.run` without explicit `check` argument
[+] 51: dev-tools/ard26_cli/detector.py:52:9 - S110: `try`-`except`-`pass` detected, consider logging the exception
[+] 52: dev-tools/ard26_cli/detector.py:52:16 - BLE001: Do not catch blind exception: `Exception`
[+] 53: dev-tools/ard26_cli/detector.py:57:34 - UP006: Use `list` instead of `List` for type annotation
[+] 54: dev-tools/ard26_cli/detector.py:57:39 - UP006: Use `dict` instead of `Dict` for type annotation
[+] 55: dev-tools/ard26_cli/detector.py:62:19 - UP022: Prefer `capture_output` over sending `stdout` and `stderr` to `PIPE`
[+] 56: dev-tools/ard26_cli/detector.py:62:19 - PLW1510: `subprocess.run` without explicit `check` argument
[+] 57: dev-tools/ard26_cli/detector.py:105:9 - S110: `try`-`except`-`pass` detected, consider logging the exception
[+] 58: dev-tools/ard26_cli/detector.py:105:16 - BLE001: Do not catch blind exception: `Exception`
[+] 59: dev-tools/ard26_cli/detector.py:114:19 - UP022: Prefer `capture_output` over sending `stdout` and `stderr` to `PIPE`
[+] 60: dev-tools/ard26_cli/detector.py:114:19 - PLW1510: `subprocess.run` without explicit `check` argument
[+] 61: dev-tools/ard26_cli/detector.py:121:21 - PLW1510: `subprocess.run` without explicit `check` argument
[+] 62: dev-tools/ard26_cli/detector.py:123:28 - UP022: Prefer `capture_output` over sending `stdout` and `stderr` to `PIPE`
[+] 63: dev-tools/ard26_cli/detector.py:123:28 - PLW1510: `subprocess.run` without explicit `check` argument
[+] 64: dev-tools/ard26_cli/detector.py:130:16 - BLE001: Do not catch blind exception: `Exception`
[A] 65: dev-tools/ard26_cli/detector.py:135:36 - UP045: Use `X | None` for type annotations
[A] 66: dev-tools/ard26_cli/detector.py:148:15 - F541: f-string without any placeholders
[A] 67: dev-tools/ard26_cli/detector.py:150:15 - F541: f-string without any placeholders
[+] 68: dev-tools/ard26_cli/detector.py:161:21 - S110: `try`-`except`-`pass` detected, consider logging the exception
[+] 69: dev-tools/ard26_cli/detector.py:161:28 - BLE001: Do not catch blind exception: `Exception`
[A] 70: dev-tools/ard26_cli/detector.py:167:49 - UP045: Use `X | None` for type annotations
[+] 71: dev-tools/ard26_cli/detector.py:186:13 - S110: `try`-`except`-`pass` detected, consider logging the exception
[+] 72: dev-tools/ard26_cli/detector.py:186:20 - BLE001: Do not catch blind exception: `Exception`
[+] 73: dev-tools/ard26_cli/detector.py:196:13 - S110: `try`-`except`-`pass` detected, consider logging the exception
[+] 74: dev-tools/ard26_cli/detector.py:196:20 - BLE001: Do not catch blind exception: `Exception`
[A] 75: dev-tools/ard26_cli/detector.py:202:38 - UP045: Use `X | None` for type annotations
[A] 76: dev-tools/ard26_cli/logger.py:5:8 - F401: `os` imported but unused
[+] 77: dev-tools/ard26_cli/logger.py:26:13 - S110: `try`-`except`-`pass` detected, consider logging the exception
[+] 78: dev-tools/ard26_cli/logger.py:26:20 - BLE001: Do not catch blind exception: `Exception`
[+] 79: dev-tools/ard26_cli/logger.py:38:16 - BLE001: Do not catch blind exception: `Exception`
[+] 80: dev-tools/ard26_cli/logger.py:46:9 - S110: `try`-`except`-`pass` detected, consider logging the exception
[+] 81: dev-tools/ard26_cli/logger.py:46:16 - BLE001: Do not catch blind exception: `Exception`
[A] 82: dev-tools/ard26_cli/telemetry.py:5:8 - F401: `os` imported but unused
[+] 83: dev-tools/ard26_cli/telemetry.py:91:16 - BLE001: Do not catch blind exception: `Exception`
[+] 84: dev-tools/ard26_cli/telemetry.py:98:9 - S110: `try`-`except`-`pass` detected, consider logging the exception
[+] 85: dev-tools/ard26_cli/telemetry.py:98:16 - BLE001: Do not catch blind exception: `Exception`
[A] 86: dev-tools/patch_io.py:2:1 - UP009: UTF-8 encoding declaration is unnecessary
[A] 87: dev-tools/patch_io.py:12:1 - I001: Import block is un-sorted or un-formatted
[+] 88: dev-tools/patch_io.py:22:9 - PLW1510: `subprocess.run` without explicit `check` argument
[+] 89: dev-tools/patch_io.py:32:9 - PLW1510: `subprocess.run` without explicit `check` argument
[A] 90: micropython/ky015_dht11.py:7:1 - I001: Import block is un-sorted or un-formatted
[A] 91: micropython/main.py:5:1 - I001: Import block is un-sorted or un-formatted
[A] 92: tools/arduino_serial_bridge.py:2:1 - UP009: UTF-8 encoding declaration is unnecessary
[A] 93: tools/arduino_serial_bridge.py:12:1 - I001: Import block is un-sorted or un-formatted
[+] 94: tools/arduino_serial_bridge.py:49:15 - PLW1510: `subprocess.run` without explicit `check` argument
[+] 95: tools/arduino_serial_bridge.py:58:13 - S110: `try`-`except`-`pass` detected, consider logging the exception
[+] 96: tools/arduino_serial_bridge.py:58:20 - BLE001: Do not catch blind exception: `Exception`
[+] 97: tools/arduino_serial_bridge.py:60:12 - BLE001: Do not catch blind exception: `Exception`
[+] 98: tools/arduino_serial_bridge.py:121:24 - BLE001: Do not catch blind exception: `Exception`
[A] 99: tools/serial_monitor.py:2:1 - UP009: UTF-8 encoding declaration is unnecessary
[A] 100: tools/serial_monitor.py:11:1 - I001: Import block is un-sorted or un-formatted
[A] 101: tools/serial_monitor.py:15:21 - F401: `pathlib.Path` imported but unused
[+] 102: tools/serial_monitor.py:51:16 - BLE001: Do not catch blind exception: `Exception`
[+] 103: tools/serial_monitor.py:68:16 - BLE001: Do not catch blind exception: `Exception`
[A] 104: tools/serial_monitor.py:94:11 - F541: f-string without any placeholders
[A] 105: tools/serial_monitor.py:95:11 - F541: f-string without any placeholders
[+] 106: tools/serial_monitor.py:103:12 - BLE001: Do not catch blind exception: `Exception`

<!-- file lint_remediation_playbook.md ends -->
