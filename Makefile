# targets:
#   test   – install dev dependencies with uv and run pytest
#   run    – install the package locally with uv and run the cli across all files
#   docker – build a container image using the provided dockerfile

.PHONY: test run docker

BASE_DIR ?= $(CURDIR)
LOG_LEVEL ?= INFO

test:
	uv pip install --system . -r pyproject.toml --all-extras
	pytest -q

run:
	uv pip install --system .
	LOG_LEVEL=$(LOG_LEVEL) python -m readme_weaver.main run --all-files --base-dir $(BASE_DIR)

docker:
	docker build -t readme-weaver:latest .
