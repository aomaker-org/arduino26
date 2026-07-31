# Workspace Specification & Consolidated AI Directives (`AI.md`)
<!-- file: AI.md -->

Notice to AI Agents: This document defines mandatory operational directives,
multi-agent collaboration protocols, hardware access boundaries, inbox/outbox
workflows, and repository hygiene for all assistants operating within the
`arduino26` workspace (AGY, Gemini, Jules, Copilot, ChatGPT, and autonomous agents).

---

## 1. System Topology & Environment Boundaries

- **Primary Repository:** `arduino26` (`/home/fekerr/src/arduino26`)
- **Primary Linux Runtime:** WSL2 / Ubuntu 26.04 / 24.04 LTS (Bash environment)
- **Host System:** Windows 11 64-bit Workstation Architecture
- **Host Interop & Callouts:** Windows native functionality accessed via `cmd.exe`
  and `pwsh.exe` (e.g., `usbipd.exe` USB passthrough, `Get-PnpDevice` PowerShell PnP queries).
- **Python Execution:** Managed via local `.venv` (`uv` or `python3 -m venv`).
  Always source `config_env` to set up environment variables and tool paths.
- **Target Hardware Focus:** Arduino Uno (ATmega328P with CH340 / FT232 / CP210x / 16U2
  USB-to-Serial bridge), expanders, microcontrollers, and embedded platforms.

---

## 2. Multi-Agent Co-Existence & Scope Boundaries

| Agent | Scope & Role | Permitted Workspace Paths |
| :--- | :--- | :--- |
| **Gemini (Web UI)** | Architectural design, refactoring, context transfer via clipboard. | `agy/inbox/`, `agy/outbox/`, `AI.md` |
| **AGY (CLI Tool)** | Local telemetry logging, command execution, task sequencing. | `agy/log/`, `agy/scratch/`, `tools/` |
| **Jules (Google)** | Asynchronous features, background automated testing, PR generation. | `.jules/` (git-ignored) |
| **Copilot / IDE** | Real-time inline edits, VS Code / Arduino IDE integration. | Standard Git tracking paths |

---

## 3. Communication & Context Transfer Protocols

- **AGY Inbox / Outbox & Logging Standard:**
  - Check `./agy/inbox/` on every turn for incoming directive files. Ingest and
    move to `./agy/inbox/archive/` with collision-free timestamps.
  - Active turn status reports are generated in `./agy/outbox/` (e.g.,
    `agy_nnn_turn_report.md` or `gemini_nnn_status_report.md`).
  - Archived outbox reports are moved to `./agy/outbox/archive/` with read-only
    locks (`chmod 444`).
  - Conversation logs and prompt/response exchanges are saved under `./agy/log/`.
- **Clipboard & Context Exchange (`files2clip` / `clip2files`):**
  - Use `files2clip` to pack workspace assets for LLM context exchange (with
    automatic 250 KB overflow protection writing to `agy/scratch/`).
  - Use `clip2files` to extract multi-file manifests pasted from Web UIs (like
    gemini.google.com).
- **Heredoc Protocol:** Always quote heredoc delimiters (`cat << 'EOF' > file`) to
  prevent shell evaluation of variables and backticks.

---

## 4. Hardware Access & WSL2 Interop Directives

- **CH340 & USB-to-Serial Driver Interop:**
  - WSL2 does not automatically attach host USB devices by default.
  - To bridge physical USB devices (CH340/ATmega328P) from Windows 11 host to WSL2,
    use `usbipd-win`:
    1. PowerShell: `pwsh.exe -Command "usbipd list"`
    2. Attach device: `pwsh.exe -Command "usbipd attach --wsl --busid <BUSID>"`
  - Verify device binding in WSL2 via `lsusb` or `tools/arduino_serial_bridge.py`.
- **Command Line Tooling:**
  - Primary compilation & flashing toolchain: `arduino-cli`.
  - Alternative environments: AVR GCC / Makefile, Rust `avr-hal`, MicroPython,
    and raw Assembly (`nasm` / `gas` / `avr-gcc`).

---

## 5. Line Wrapping & Formatting Standards

- **Prose & Markdown:** Wrap documentation, comments, and text files to **80 columns**
  (hard max of 120 columns) for clean terminal rendering and diffs.
- **Source Code:** Standard formatting per language, keeping lines within 80–120
  columns where practical.
- **Single-Line Copy-Paste Commands:** Format terminal commands on their own isolated
  single-line code blocks so users can easily triple-click to select and copy without line breaks.
- **Mandatory File Headers & Footers:**
  - Header: Every text file must begin with a comment specifying the file path:
    `<!-- file: relative/path/filename -->` or `# file: relative/path/filename`.
  - Footer: Every text file must end with an explicit footer:
    `<!-- file relative/path/filename ends -->` or `# file relative/path/filename ends`.

---

## 6. Observability, Logging & FOSS Philosophy

- **STRICT NO PIPE TO NULL:** NEVER pipe standard output or standard error to
  `/dev/null`. Hide nothing. Route diagnostic output into timestamped logs under
  `agy/log/` or `logs/` if terminal clutter must be reduced.
- **STRICT NO UNVERIFIED CURL PIPING:** NEVER pipe `curl` or `wget` downloads directly
  into `sh` or `bash` (`curl ... | sh`). Always download to an explicit temporary file,
  verify download completion, or use official package managers (`apt`, `uv`, `pip`, `winget`).
- **Empirical Verification Required:** NEVER declare success without running
  empirical build/test verification commands (e.g. `arduino-cli compile`,
  `python3 tools/...`, `make`).
- **Aggressively FOSS:** This repository adheres to open source principles.
  All code, tools, and documentation are licensed under permissive FOSS licenses
  (MIT, Apache 2.0, Unlicense / CC0).

---

## 7. Script Management & Snippets Toolbox Directives (`tools/*` vs `dev-tools/*`)

- **Script Directory Separation:**
  - **`./tools/`**: Saved exclusively for **Arduino work** (serial scanning, sketch uploading, serial monitors, board diagnostics).
  - **`./dev-tools/`**: Saved for **WSL / Linux / Win11 helper tools** (context packing, clipboard exchange, PowerShell ExecutionPolicy wrappers, automated environment provisioning).
- **Mandatory Cataloging:** Every script added to `tools/*` or `dev-tools/*` MUST be documented in `docs/snippets_toolbox.md`.
- **Attribution & Provenance:** External web resources, datasheets, or library references MUST be attributed in script header comments and `docs/snippets_toolbox.md`.

<!-- file AI.md ends -->
