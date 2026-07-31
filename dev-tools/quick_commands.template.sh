#!/usr/bin/env bash
# ==============================================================================
# Path:        dev-tools/quick_commands.template.sh
# Purpose:     Template file containing ready-to-copy single-line commands
#              Copy or uncomment lines to customize your environment workflows.
# Target OS:   Ubuntu 24.04 / 26.04 LTS (WSL2) + Windows 11 Host
# Updated:     2026-07-31
# ==============================================================================

# ------------------------------------------------------------------------------
# 1. Environment Loading & Tagging (Triple-click any line to copy)
# ------------------------------------------------------------------------------
# source config_env
# source config_env force ard26-2nd+
# source config_env unset

# ------------------------------------------------------------------------------
# 2. Sketch Compilation Commands (ard26 CLI)
# ------------------------------------------------------------------------------
# ard26 compile
# ard26 compile uno_clone_diag
# ard26 compile sketches/ky015_dht11

# ------------------------------------------------------------------------------
# 3. Sketch Upload Commands (WSL & Windows Host Failover)
# ------------------------------------------------------------------------------
# ard26 upload
# ard26 upload uno_clone_diag -p /dev/ttyUSB0
# ard26 upload uno_clone_diag -p COM5

# ------------------------------------------------------------------------------
# 4. Interactive Serial Telemetry & Monitoring
# ------------------------------------------------------------------------------
# ard26 monitor
# ard26 monitor -b 9600
# ard26 monitor -p COM5 -b 115200

# ------------------------------------------------------------------------------
# 5. Hardware Device Scanning & Auditing
# ------------------------------------------------------------------------------
# ard26 scan
# ard26 config

# ------------------------------------------------------------------------------
# 6. Windows 11 Host Integration & USB Passthrough (Run from WSL or Win11)
# ------------------------------------------------------------------------------
# pwsh_bypass -Command "usbipd list"
# pwsh_bypass -Command "usbipd attach --wsl --busid 2-1"
# pwsh_bypass -Command "winget install Arduino.cli"

# file dev-tools/quick_commands.template.sh ends
