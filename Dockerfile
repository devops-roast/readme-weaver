# syntax=docker/dockerfile:1

FROM python:3.13-slim AS builder

RUN : \
    set -eux \
    && pip install --upgrade pip \
    && pip install "uv>=0.8.13,<1.0.0"

WORKDIR /tmp/app

COPY pyproject.toml uv.lock README.md LICENSE ./
COPY readme_weaver ./readme_weaver

RUN uv pip install --prefix /install .

FROM python:3.13-slim AS runtime

COPY --from=builder /install/ /usr/local/

ENTRYPOINT ["readme-weaver"]
