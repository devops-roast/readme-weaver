import glob
import os
import sys

import typer
from loguru import logger

from readme_weaver.include_content_reader import IncludeContentReader
from readme_weaver.include_metadata_extractor import IncludeMetadataExtractor
from readme_weaver.readme_weaver import ReadmeWeaver

"""
CLI entry point for the ReadmeWeaver tool.

This module configures logging based on an environment variable or a command line
option and exposes a ``run`` command that processes markdown files in the current
repository.  Use the ``--log-level`` option or set the ``LOG_LEVEL`` environment
variable to control the verbosity of the output.  If neither is provided, the
default level is INFO.
"""

# Remove any default handlers so logging can be configured in the ``run`` command.
logger.remove()

app = typer.Typer(rich_markup_mode=None)


@app.command(help="Embed partial markdown from external files into README files.")
def run(
    all_files: bool = typer.Option(
        False, "--all-files", help="Process all markdown files in the repository."
    ),
    changed_files: list[str] = typer.Argument(
        None, help="List of changed files to process. Use with pre‑commit."
    ),
    base_dir: str = typer.Option(
        None,
        "--base-dir",
        "-b",
        help=(
            "Base directory for resolving relative include paths. "
            "Defaults to the README_WEAVER_BASE environment variable or the current working directory."
        ),
    ),
    log_level: str = typer.Option(
        None,
        "--log-level",
        "-l",
        help=(
            "Set the logging level (e.g. DEBUG, INFO, WARNING, ERROR). "
            "If not provided, defaults to the value of the LOG_LEVEL environment variable or INFO."
        ),
    ),
):
    """
    Entry point for the CLI.  Scans all markdown files in the repository for
    include directives and updates them in place.  When used as a pre‑commit
    hook, only changed files are processed unless ``--all-files`` is passed.

    The optional ``--base-dir`` overrides the ``README_WEAVER_BASE``
    environment variable and determines how relative include paths are
    resolved.
    """
    env_level = os.environ.get("LOG_LEVEL")
    effective_level = (log_level or env_level or "INFO").upper()
    logger.remove()
    logger.add(sys.stderr, level=effective_level)

    readme_paths = glob.glob("**/*.md", recursive=True)

    if not readme_paths:
        logger.info("No markdown files found in the current repository.")
        raise typer.Exit(0)

    include_metadata_extractor = IncludeMetadataExtractor()
    include_content_reader = IncludeContentReader(base_dir=base_dir)
    files = changed_files if not all_files else None

    weaver = ReadmeWeaver(
        readme_paths=readme_paths,
        changed_files=files,
        include_metadata_extractor=include_metadata_extractor,
        include_content_reader=include_content_reader,
    )

    weaver()
    logger.info("Finished successfully.")


if __name__ == "__main__":
    app()
