# Licensing Options & Open Source Philosophy (LICENSING.md)
<!-- file: docs/LICENSING.md -->

## Aggressively Free and Open Source Software (FOSS)

The `arduino26` workspace is dedicated to open access, permissive hardware
hacking, embedded software experimentation, and transparent AI collaboration.

---

## Permitted License Models for Sub-projects & Modules

Depending on project requirements, modules within `arduino26` can select from
or dual-license under any of the following standard FOSS licenses:

### 1. MIT License (Default Workspace License)
- **Characteristics:** Highly permissive, short, simple, commercial-friendly.
- **Use Case:** Primary choice for scripts, toolchain helpers, C++ sketches, and
  utility libraries in `arduino26`.

### 2. Apache License 2.0
- **Characteristics:** Permissive, explicitly provides patent grants and protects
  contributors against patent claims.
- **Use Case:** Complex firmware frameworks, driver modules, or multi-agent
  automation scripts requiring explicit patent protection.

### 3. The Unlicense / CC0 1.0 Universal (Public Domain)
- **Characteristics:** Maximum openness. Dedicated to the public domain without
  conditions or copyright retention.
- **Use Case:** Example sketches, boilerplate code, micro-assembly templates,
  and documentation code blocks meant to be copied freely.

### 4. GNU General Public License v3.0 (GPL-3.0)
- **Characteristics:** Copyleft. Ensures downstream modifications and derivative
  works remain free and open source.
- **Use Case:** Standalone embedded applications where open source propagation is
  strictly mandated.

---

## Dual Licensing & Contributor Guidelines

- All contributions made to this repository are provided under open FOSS terms.
- Source files should specify their license in the file header (e.g., SPDX identifier):
  ```cpp
  // SPDX-License-Identifier: MIT
  ```

<!-- file docs/LICENSING.md ends -->
