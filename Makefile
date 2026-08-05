# file: Makefile
# Purpose: Makefile to organize workspace tasks like linting
# Target OS: Ubuntu 24.04 / 26.04 LTS (WSL2) + Windows 11 Host

.PHONY: help lint lint-python lint-ino lint-fix

help:
	@echo "Available Makefile targets:"
	@echo "  make lint         - Run lint checks on all files (Python + Arduino sketches)"
	@echo "  make lint-python  - Run ruff check on python files"
	@echo "  make lint-ino     - Compile Arduino sketches to verify syntax/compilation"
	@echo "  make lint-fix     - Run ruff check --fix to auto-resolve python violations"
	@echo "  make help         - Show this help menu"

lint: lint-python lint-ino

lint-python:
	uvx ruff check .

lint-ino:
	@for sketch in sketches/*/; do \
		echo "Checking sketch: $$sketch"; \
		arduino-cli compile --fqbn arduino:avr:uno "$$sketch" || exit 1; \
	done

lint-fix:
	uvx ruff check . --fix

# file Makefile ends


