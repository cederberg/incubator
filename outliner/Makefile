.PHONY: all clean test outdated publish

all:
	@echo 'Makefile commands'
	@grep -E -A 1 '^#' Makefile | awk 'BEGIN { RS = "--\n"; FS = "\n" }; { sub("#+ +", "", $$1); sub(":.*", "", $$2); printf " · make %-18s- %s\n", $$2, $$1}'
	@echo
	@echo 'Release: make clean test publish'

# Remove build artifacts
clean:
	rm -rf dist build src/*.egg-info

# Run tests
test:
	uv run pytest

# List outdated dependencies and toolchain
outdated:
	@echo --== python toolchain ==--
	@uv run python --version
	@echo
	@echo --== dependencies ==--
	@uv run pip list --outdated

# Build and publish to PyPI
publish: clean test
	uv build
	uv publish
