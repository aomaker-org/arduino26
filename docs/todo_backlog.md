# Workspace TODO & Backlog Registry (`docs/todo_backlog.md`)
<!-- file: docs/todo_backlog.md -->

This file tracks planned features, architectural considerations, and open backlog items for the `arduino26` workspace. It is primarily **append-only**, with items marked off as they progress.

---

## 🔑 Status Character Markers Key

| Marker | Status Meaning | Description |
| :---: | :--- | :--- |
| `[ ]` | **Unscheduled** | Not currently prioritized; candidate for future turns. |
| `[+]` | **High Priority** | Planned for immediate or near-term implementation. |
| `[!]` | **Critical / Must-Do** | Essential requirement, safety fix, or blocking task. |
| `[*]` | **In Progress** | Active turn task currently being implemented. |
| `[x]` | **Completed** | Fully implemented, verified, and committed. |
| `[-]` | **Won't Do / Deferred** | Explicitly evaluated and declined or postponed indefinitely. |
| `[?]` | **Under Evaluation** | Architectural consideration or research item under review. |

---

## 📋 Workspace Backlog Registry

### Item #001: [?] Incremental Build Caching & Makefile Interop
- **Category:** Build System & Compilation Performance
- **Date Added:** 2026-07-31
- **Status:** `[?]` Under Evaluation (Research & Design Phase)
- **Problem Statement:** Standard `arduino-cli compile` invocations can incur redundant compilation overhead on unchanged sketch source files (`.ino`, `.cpp`, `.h`). For rapid hardware iteration, avoiding recompilation when source files have not been modified speeds up upload cycles.
- **Best Practices Analysis & Architecture Options:**
  - **Option A (GNU `Makefile` System):** Provide a `Makefile` wrapper utilizing `avr-gcc` object rules (`%.o: %.cpp`) or `arduino-cli compile --build-path` dependency rules. Allows Unix-native `make` workflows.
  - **Option B (`arduino-cli --build-path` Persistent Cache):** Configure `ard26 compile` to output build artifacts to a deterministic directory (`.build/<sketch_name>/`). `arduino-cli` natively reuses compiled object files (`.o`) from `--build-path` if source files are unchanged.
  - **Option C (`ard26` Source Timestamp / SHA256 Guard):** Add an mtime or SHA256 hash check in `ard26_cli/cli.py`. If source `.ino` / `.h` files are older than `.build/<sketch>/<sketch>.hex`, skip `arduino-cli compile` entirely unless `--force` is specified.
- **Recommended Best-Practice Approach:** Combine **Option B** and **Option C** inside `ard26` CLI (using `--build-path .build/<sketch>`) so incremental builds complete in milliseconds without custom toolchains, while providing a clean `Makefile` snippet under `dev-tools/` for Makefile enthusiasts.

---

### Item #002: [+] Expand Sensor Sketch & Telemetry Suite
- **Category:** Hardware Drivers & Sketches
- **Date Added:** 2026-07-31
- **Status:** `[+]` High Priority
- **Description:** Add support and test sketches for KY-015 / DHT11, DS18B20 1-Wire temperature sensors, and I2C 1602 LCD displays with UTF-8 serial telemetry output.

---

### Item #003: [ ] MicroPython Flashing Integration (`mpremote`)
- **Category:** Microcontroller Runtimes
- **Date Added:** 2026-07-31
- **Status:** `[ ]` Unscheduled
- **Description:** Integrate `mpremote` subcommands into `ard26` CLI (`ard26 py-upload`, `ard26 py-repl`) for ESP32 / RP2040 MicroPython boards.

---

### Item #004: [ ] Automated GitHub Actions CI Workflow
- **Category:** DevOps & Testing
- **Date Added:** 2026-07-31
- **Status:** `[ ]` Unscheduled
- **Description:** Add `.github/workflows/compile.yml` to automatically run `ard26 compile` on all sketches in PRs.

---

<!-- file docs/todo_backlog.md ends -->
