# file: Makefile
# Purpose: Makefile to organize workspace tasks like linting
# Target OS: Ubuntu 24.04 / 26.04 LTS (WSL2) + Windows 11 Host

.PHONY: lint lint-fix

lint:
	uvx ruff check .

lint-fix:
	uvx ruff check . --fix

# file Makefile ends
