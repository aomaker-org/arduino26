# file: Makefile
# Purpose: Makefile to organize workspace tasks like linting
# Target OS: Ubuntu 24.04 / 26.04 LTS (WSL2) + Windows 11 Host

# Makefile Pipeline Configuration
# Precedence hierarchy:
# 1. Command-line environment override: 'make run ARD26_MAKE_USES_ARD26=1'
# 2. Shell Environment variable: 'export ARD26_MAKE_USES_ARD26=1'
# 3. Local configuration file: 'tools.make_uses_ard26' in 'arduino_config.toml'
# 4. Default: 0 (Direct python module execution: 'python3 -m ard26_cli.cli')

# Read tools.make_uses_ard26 from arduino_config.toml if it exists
TOML_SETTING := $(shell grep -oP "(?<=make_uses_ard26 = )\w+" arduino_config.toml 2>/dev/null)
ifeq ($(TOML_SETTING),true)
    CONFIG_VAL = 1
else
    CONFIG_VAL = 0
endif

# Apply environment override fallback (hierarchy precedence)
ARD26_MAKE_USES_ARD26 ?= $(CONFIG_VAL)

# Determine run execution command based on precedence result
ifeq ($(ARD26_MAKE_USES_ARD26),1)
    RUN_CMD = ard26
else
    RUN_CMD = python3 -m ard26_cli.cli
endif

.PHONY: help lint lint-python lint-ino lint-hygiene lint-fix compile upload monitor run

help:
	@echo "Available Makefile targets:"
	@echo "  make lint         - Run all checks (Python, sketches compilation, & hygiene)"
	@echo "  make lint-python  - Run ruff check on python files"
	@echo "  make lint-ino     - Compile Arduino sketches to verify syntax/compilation"
	@echo "  make lint-hygiene - Lint workspace file headers, footers and column widths"
	@echo "  make lint-fix     - Run ruff check --fix to auto-resolve python violations"
	@echo "  make compile      - Compile the default sketch (or specify SKETCH=name)"
	@echo "  make upload       - Compile and upload sketch"
	@echo "  make monitor      - Launch interactive serial monitor"
	@echo "  make run          - Execute pipeline: Compile -> Upload -> Monitor"
	@echo "  make help         - Show this help menu"
	@echo ""
	@echo "Configuration settings:"
	@echo "  ARD26_MAKE_USES_ARD26=$(ARD26_MAKE_USES_ARD26) (Set to 1 to use 'ard26' command alias)"
	@echo ""
	@echo "=========================================================="
	@echo "    Summary of 'docs/ard26_cli_guide.md' for CLI Tool"
	@echo "=========================================================="
	@cat docs/ard26_cli_guide.md | head -n 35
	@echo "..."

compile:
	$(RUN_CMD) compile $(SKETCH)

upload:
	$(RUN_CMD) upload $(SKETCH)

monitor:
	$(RUN_CMD) monitor

run:
	$(RUN_CMD) run $(SKETCH)

lint: lint-python lint-ino lint-hygiene

lint-python:
	uvx ruff check .

lint-ino:
	@for sketch in sketches/*/; do \
		echo "Checking sketch: $$sketch"; \
		arduino-cli compile --fqbn arduino:avr:uno "$$sketch" || exit 1; \
	done

lint-hygiene:
	python3 dev-tools/lint_hygiene.py

lint-fix:
	uvx ruff check . --fix

# file Makefile ends
