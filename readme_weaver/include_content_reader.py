"""
Content reader for include directives.

Given a list of ``IncludeMetadata`` objects produced by the extractor, this
reader resolves the include paths, reads the referenced files, and prepares the
replacement text.  Each include block will receive a warning comment to
discourage manual edits to the generated region.

Relative paths are resolved relative to a base directory, which can be
specified via the ``base_dir`` argument or the ``README_WEAVER_BASE``
environment variable.  Absolute paths are used as‑is.
"""

from typing import Protocol, List
from pathlib import Path
import os

from .include_metadata import IncludeMetadata


class IncludeContentReaderInterface(Protocol):
    """Interface for reading include content and updating metadata objects."""

    def read(self, includes: List[IncludeMetadata]) -> List[IncludeMetadata]: ...


class IncludeContentReader:
    """
    Read the contents of each include directive and prepare the text to be
    inserted into the README.

    For each ``IncludeMetadata`` instance returned by the extractor, this
    reader resolves the file path, reads the file, and prefixes the
    content with an auto‑generated notice.  If an include is marked
    ``required`` and the file does not exist, a ``FileNotFoundError`` is
    raised.  Otherwise, the content is set to an empty string.
    """

    def __init__(self, base_dir: str | None = None) -> None:
        # Determine base directory for relative include paths.  If provided
        # explicitly, use that; otherwise use README_WEAVER_BASE environment
        # variable or default to current working directory.
        self._base_dir = Path(
            base_dir or os.environ.get("README_WEAVER_BASE", ".")
        ).resolve()

    def read(self, includes: List[IncludeMetadata]) -> List[IncludeMetadata]:
        processed: List[IncludeMetadata] = []
        for inc in includes:
            if inc.extraction_type != "include":
                raise ValueError(f"Unsupported extraction type {inc.extraction_type}.")
            inc_path = Path(inc.path)
            full_path = (
                inc_path if inc_path.is_absolute() else (self._base_dir / inc_path)
            )
            if not full_path.exists():
                if inc.required:
                    raise FileNotFoundError(
                        f"Include file {inc.path} not found (resolved to {full_path})."
                    )
                inc.content = ""
                processed.append(inc)
                continue
            text = full_path.read_text(encoding="utf-8")
            # Prepend auto‑generated notice if there is any content
            if text:
                text = "<!-- content below is auto-generated; do not edit -->\n" + text
            inc.content = text
            processed.append(inc)
        return processed
