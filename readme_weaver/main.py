import glob
import sys

import typer
from loguru import logger

from readme_weaver.readme_weaver import ReadmeWeaver
from readme_weaver.include_content_reader import IncludeContentReader
from readme_weaver.include_metadata_extractor import IncludeMetadataExtractor

logger.remove()
logger.add(sys.stderr, level="DEBUG")

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
):
    """
    Entry point for the CLI.  Scans all markdown files in the repository for
    include directives and updates them in place.  When used as a pre‑commit
    hook, only changed files are processed unless ``--all-files`` is passed.

    The optional ``--base-dir`` overrides the ``README_WEAVER_BASE``
    environment variable and determines how relative include paths are
    resolved.
    """
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
