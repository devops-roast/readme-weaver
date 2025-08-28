# targets:
#   test   - run all unit tests using poetry
#   run    - execute the readme weaver cli on all markdown files
#   docker - build the docker image using the provided dockerfile

.PHONY: test run docker

BASE_DIR ?= $(CURDIR)
LOG_LEVEL ?= INFO

test:
	poetry run pytest -q

run:
	LOG_LEVEL=$(LOG_LEVEL) poetry run readme-weaver run --all-files --base-dir $(BASE_DIR)

docker:
	docker build -t readme-weaver:latest .
