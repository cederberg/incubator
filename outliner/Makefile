.PHONY: all clean test outdated publish

all:
	@echo 'Makefile commands'
	@grep -E -A 1 '^#' Makefile | awk 'BEGIN { RS = "--\n"; FS = "\n" }; { sub("#+ +", "", $$1); sub(":.*", "", $$2); printf " · make %-18s- %s\n", $$2, $$1}'
	@echo
	@echo 'Release: make clean test publish'

# Remove build artifacts
clean:
	rm -rf .pytest_cache .venv build dist
	find . -type d \( -name __pycache__ -o -name '*.egg-info' \) -prune -exec rm -rf {} +
	find . -name '*.py[cod]' -delete

# Run tests
test:
	uv run pytest

# List outdated dependencies and toolchain
outdated:
	@echo --== python toolchain ==--
	@uv run python --version
	@echo
	@echo --== dependencies ==--
	@uv pip list --outdated

# Build and publish to PyPI
publish: clean test
	uv build
	uv publish
