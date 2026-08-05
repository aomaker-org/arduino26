# file: Makefile
# Purpose: Makefile to organize workspace tasks like linting
# Target OS: Ubuntu 24.04 / 26.04 LTS (WSL2) + Windows 11 Host

.PHONY: help lint lint-fix

help:
	@echo "Available Makefile targets:"
	@echo "  make lint      - Run ruff check on python files"
	@echo "  make lint-fix  - Run ruff check --fix to auto-resolve violations"
	@echo "  make help      - Show this help menu"

lint:
	uvx ruff check .

lint-fix:
	uvx ruff check . --fix

# file Makefile ends

