# syntax=docker/dockerfile:1

FROM python:3.13-slim AS base

RUN pip install --upgrade pip \
    && pip install "uv>=0.8.13"

WORKDIR /app

COPY pyproject.toml README.md ./
COPY readme_weaver ./readme_weaver

RUN uv pip install --system .

ENTRYPOINT ["readme-weaver"]
